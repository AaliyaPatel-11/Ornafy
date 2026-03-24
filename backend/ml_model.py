import pandas as pd
from sklearn.linear_model import LinearRegression

# Training dataset
data = {
    "jewelry_type": ["Ring","Ring","Ring","Necklace","Bracelet","Earrings"],
    "metal_type": ["Gold","Silver","Platinum","Gold","Silver","Gold"],
    "stone_type": ["Diamond","Ruby","Emerald","Diamond","Ruby","No Stone"],
    "price": [65000,25000,85000,70000,30000,40000]
}

df = pd.DataFrame(data)

# Encode features
df_encoded = pd.get_dummies(df[["jewelry_type","metal_type","stone_type"]])

# Train model
model = LinearRegression()
model.fit(df_encoded, df["price"])

def predict_price(jewelry, metal, stone):

    input_df = pd.DataFrame({
        "jewelry_type":[jewelry],
        "metal_type":[metal],
        "stone_type":[stone]
    })

    input_encoded = pd.get_dummies(input_df)

    input_encoded = input_encoded.reindex(columns=df_encoded.columns, fill_value=0)

    prediction = model.predict(input_encoded)[0]

    return int(prediction)