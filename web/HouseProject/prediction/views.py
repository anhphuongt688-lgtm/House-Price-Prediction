from django.shortcuts import render
import joblib
import pandas as pd
import numpy as np
import os
from django.conf import settings

# 1. Load Model (Chỉ load 1 lần khi server chạy để đỡ tốn Ram)
# Đường dẫn tới file pkl
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'prediction/ml_models/housing_model.pkl')
ZIP_PATH = os.path.join(BASE_DIR, 'prediction/ml_models/zip_ppsf.pkl')
COORD_PATH = os.path.join(BASE_DIR, 'prediction/ml_models/center_coords.pkl')

model = joblib.load(MODEL_PATH)
zip_ppsf_dict = joblib.load(ZIP_PATH)
center_coords = joblib.load(COORD_PATH)


def index(request):
    result = None

    if request.method == 'POST':
        # 2. Lấy dữ liệu từ Form HTML gửi lên
        try:
            # Lấy các trường thông tin cơ bản
            sqft_living = float(request.POST.get('sqft_living'))
            sqft_lot = float(request.POST.get('sqft_lot'))
            bedrooms = int(request.POST.get('bedrooms'))
            bathrooms = float(request.POST.get('bathrooms'))
            floors = float(request.POST.get('floors'))

            # Lấy thông tin vị trí & chất lượng
            zipcode = int(request.POST.get('zipcode'))  # Lưu ý: Form gửi về string
            lat = float(request.POST.get('lat'))
            long = float(request.POST.get('long'))
            grade = int(request.POST.get('grade'))
            condition = int(request.POST.get('condition'))
            view = int(request.POST.get('view'))
            waterfront = int(request.POST.get('waterfront'))

            # Lấy thông tin khác
            sqft_basement = float(request.POST.get('sqft_basement'))
            sqft_lot15 = float(request.POST.get('sqft_lot15'))
            yr_built = int(request.POST.get('yr_built'))
            yr_renovated = int(request.POST.get('yr_renovated'))

            # 3. FEATURE ENGINEERING (Xử lý giống hệt lúc training)
            # Tính tuổi nhà
            house_age = 2015 - yr_built
            # Đã sửa chữa chưa
            was_renovated = 1 if yr_renovated > 0 else 0
            # Khoảng cách tâm
            distance = np.sqrt((lat - center_coords['lat']) ** 2 + (long - center_coords['long']) ** 2)
            # Zipcode ppsf (Xử lý nếu zipcode lạ)
            zip_val = zip_ppsf_dict.get(zipcode)
            if zip_val is None:
                # Thử tìm theo string nếu key là string
                zip_val = zip_ppsf_dict.get(str(zipcode))
            if zip_val is None:
                # Lấy trung bình
                zip_val = np.mean(list(zip_ppsf_dict.values()))
            zip_avg_ppsf = zip_val

            # 4. Tạo DataFrame input (Đúng thứ tự cột)
            input_data = pd.DataFrame({
                'bedrooms': [bedrooms], 'bathrooms': [bathrooms],
                'sqft_living': [sqft_living], 'sqft_lot': [sqft_lot],
                'floors': [floors], 'waterfront': [waterfront],
                'view': [view], 'condition': [condition],
                'grade': [grade], 'sqft_basement': [sqft_basement],
                'lat': [lat], 'long': [long],
                'sqft_lot15': [sqft_lot15], 'house_age': [house_age],
                'was_renovated': [was_renovated], 'distance': [distance],
                'zip_avg_ppsf': [zip_avg_ppsf]
            })

            # 5. Dự báo
            pred_log = model.predict(input_data)[0]
            price = np.exp(pred_log)  # Chuyển Log -> Giá thực

            # Format tiền cho đẹp
            result = f"{price:,.2f} USD"

        except Exception as e:
            result = f"Lỗi nhập liệu: {str(e)}"

    return render(request, 'index.html', {'result': result})