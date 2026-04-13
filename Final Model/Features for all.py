import pandas as pd
import numpy as np
import os

# =============================
# PARAMETERS
# =============================
STOP_VEL = 2
MIN_STOP_FRAMES = 72
FPS = 24
POST_WINDOW = 10
PRE_WINDOW = 10

# =============================
# CLASS MAPPINGS
# =============================
HARD_ID_TO_CLASS = {
    7: "car",
    8: "car",
    1: "car",
    5: "motor",
    6: "truck",
    11: "van",
    9: "van"
}

CLASS_MAP = {
    "bicycle": 0,
    "bus": 1,
    "car": 2,
    "motor": 3,
    "pedestrian": 4,
    "people": 5,
    "tricycle": 6,
    "truck": 7,
    "van": 8
}

VALID_CLASSES = {
    "car",
    "motor",
    "tricycle",
    "truck",
    "van"
}

# =============================
# HELPER FUNCTIONS
# =============================

def compute_displacement(x, y):
    return np.sqrt((x[-1] - x[0])**2 + (y[-1] - y[0])**2)


def extract_stop_segments(df):
    vel = np.abs(df["Smoothed_vel(kmph)"].values)
    is_stop = vel < STOP_VEL

    segments = []
    start = None

    for i, val in enumerate(is_stop):
        if val and start is None:
            start = i
        elif not val and start is not None:
            end = i - 1
            if (end - start + 1) >= MIN_STOP_FRAMES:
                segments.append((start, end))
            start = None

    if start is not None:
        end = len(df) - 1
        if (end - start + 1) >= MIN_STOP_FRAMES:
            segments.append((start, end))

    return segments


def compute_features(df, start, end, vehicle_class, class_id):
    segment = df.iloc[start:end+1]

    x = segment["xc"].values
    y = segment["yc"].values
    vel = np.abs(segment["Smoothed_vel(kmph)"].values)

    duration_frames = end - start + 1
    duration_sec = duration_frames / FPS
    pos_variance = np.var(x) + np.var(y)

    displacement = compute_displacement(x, y)
    stop_mask = vel < 0.5  # stricter threshold
    x_stop = x[stop_mask]
    y_stop = y[stop_mask]

    if len(x_stop) > 1:
        pos_variance_stop = np.var(x_stop) + np.var(y_stop)
    else:
        pos_variance_stop = pos_variance  # fallback to original

    mean_vel = np.mean(vel)
    max_vel = np.max(vel)

    mean_x = np.mean(x)
    mean_y = np.mean(y)

    pre_start = max(0, start - PRE_WINDOW)
    post_end = min(len(df) - 1, end + POST_WINDOW)

    pre_vel = np.mean(np.abs(df.iloc[pre_start:start]["Smoothed_vel(kmph)"])) if start > 0 else 0

    # IMPORTANT: use MAX instead of MEAN
    post_vel = np.max(np.abs(df.iloc[end+1:post_end+1]["Smoothed_vel(kmph)"])) if end < len(df)-1 else 0

    return {
        "class": vehicle_class,
        "class_id": class_id,

        "start_frame": int(df.iloc[start]["Frame"]),
        "end_frame": int(df.iloc[end]["Frame"]),

        "duration_frames": duration_frames,
        "duration_sec": duration_sec,

        "displacement": displacement,
        "pos_variance": pos_variance_stop,

        "mean_vel": mean_vel,
        "max_vel": max_vel,

        "pre_vel": pre_vel,
        "post_vel": post_vel,

        "mean_x": mean_x,
        "mean_y": mean_y
    }


# =============================
# MOMENTARY STOP PIPELINE
# =============================

def process_vehicle_csv(file_path):
    try:
        df = pd.read_csv(file_path)

        df.columns = df.columns.str.strip().str.lower()

        required_cols = ["frame", "smoothed_cls", "smoothed_vel(kmph)", "xc", "yc"]
        for col in required_cols:
            if col not in df.columns:
                print(f"\nMissing '{col}' in {file_path}")
                return pd.DataFrame()

        df = df.sort_values("frame").reset_index(drop=True)

        if df.empty:
            return pd.DataFrame()

        vehicle_class = df.iloc[0]["smoothed_cls"]

        if vehicle_class not in VALID_CLASSES:
            return pd.DataFrame()

        class_id = CLASS_MAP.get(vehicle_class, -1)

        df["Smoothed_vel(kmph)"] = df["smoothed_vel(kmph)"]
        df["Frame"] = df["frame"]

        stop_segments = extract_stop_segments(df)

        features_list = []

        for (start, end) in stop_segments:
            features = compute_features(df, start, end, vehicle_class, class_id)
            features["vehicle_file"] = os.path.basename(file_path)
            features_list.append(features)

        return pd.DataFrame(features_list)

    except Exception as e:
        print(f"\nError in file: {file_path}")
        print(e)
        return pd.DataFrame()


def process_all_csv(folder_path):
    all_features = []

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            path = os.path.join(folder_path, file)
            df_features = process_vehicle_csv(path)

            if not df_features.empty:
                all_features.append(df_features)

    if all_features:
        return pd.concat(all_features, ignore_index=True)
    else:
        return pd.DataFrame()


# =============================
# HARD STOP PIPELINE
# =============================

def process_hard_stop_csv(file_path):
    try:
        df = pd.read_csv(file_path)

        df.columns = df.columns.str.strip().str.lower()

        required_cols = ["frame", "xc", "yc", "class_id"]
        for col in required_cols:
            if col not in df.columns:
                print(f"\nMissing '{col}' in {file_path}")
                return pd.DataFrame()

        if "smoothed_vel(kmph)" in df.columns:
            df["Smoothed_vel(kmph)"] = df["smoothed_vel(kmph)"]
        elif "velocity" in df.columns:
            df["Smoothed_vel(kmph)"] = df["velocity"]
        else:
            print(f"\nNo velocity column in {file_path}")
            return pd.DataFrame()

        df = df.sort_values("frame").reset_index(drop=True)

        if df.empty:
            return pd.DataFrame()

        raw_id = df.iloc[0]["class_id"]
        vehicle_class = HARD_ID_TO_CLASS.get(raw_id, None)

        if vehicle_class not in VALID_CLASSES:
            return pd.DataFrame()

        class_id = CLASS_MAP.get(vehicle_class, -1)

        df["Frame"] = df["frame"]

        # Entire file = one stop
        start = 0
        end = len(df) - 1

        features = compute_features(df, start, end, vehicle_class, class_id)
        features["vehicle_file"] = os.path.basename(file_path)

        return pd.DataFrame([features])

    except Exception as e:
        print(f"\nError in HARD file: {file_path}")
        print(e)
        return pd.DataFrame()


def process_all_hard_csv(folder_path):
    all_features = []

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            path = os.path.join(folder_path, file)
            df_features = process_hard_stop_csv(path)

            if not df_features.empty:
                all_features.append(df_features)

    if all_features:
        return pd.concat(all_features, ignore_index=True)
    else:
        return pd.DataFrame()


# =============================
# USAGE
# =============================

momentary_folder = "SORTED_DATA"
hard_folder = "hard_stop_data"

df_momentary = process_all_csv(momentary_folder)
df_hard = process_all_hard_csv(hard_folder)

final_df = pd.concat([df_momentary, df_hard], ignore_index=True)

final_df.to_csv("final_stop_features.csv", index=False)