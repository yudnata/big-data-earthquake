from pyspark.ml.feature import VectorAssembler, StandardScaler
from config.settings import FEATURE_COLS, RAW_FEATURES_COL, SCALED_FEATURES_COL

def build_features(df):
    assembler = VectorAssembler(
        inputCols=FEATURE_COLS,
        outputCol=RAW_FEATURES_COL,
        handleInvalid="skip"
    )
    df_assembled = assembler.transform(df)
    
    scaler = StandardScaler(
        inputCol=RAW_FEATURES_COL,
        outputCol=SCALED_FEATURES_COL,
        withMean=True,
        withStd=True
    )
    scaler_model = scaler.fit(df_assembled)
    df_scaled = scaler_model.transform(df_assembled)
    
    return df_scaled
