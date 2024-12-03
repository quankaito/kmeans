import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class Clustering:
    """
    Lớp Clustering thực hiện phân cụm dữ liệu dựa trên các đặc trưng đầu vào. 
    Sử dụng thuật toán K-Means và tiền xử lý dữ liệu bằng StandardScaler.

    Các tham số:
    ----------
    n_clusters : int, mặc định = 3
        Số lượng cụm (cluster) cần phân chia.

    Thuộc tính:
    ----------
    model : KMeans
        Mô hình K-Means được sử dụng để phân cụm.
    scaler : StandardScaler
        Công cụ chuẩn hóa dữ liệu, đưa các đặc trưng về cùng một khoảng giá trị.

    Phương thức:
    ----------
    fit_predict(data):
        Thực hiện tiền xử lý, phân cụm dữ liệu và trả về DataFrame kết quả.

        Tham số:
        -------
        data : dict hoặc list
            Dữ liệu đầu vào cần phân cụm, chứa các cột đặc trưng như "rating" và "review_count".

        Trả về:
        -------
        pandas.DataFrame
            DataFrame chứa dữ liệu gốc, các đặc trưng sau khi chuẩn hóa và nhãn cụm (cluster).
    """
    
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
    
    def fit_predict(self, data):
        """
        Thực hiện phân cụm dữ liệu dựa trên các đặc trưng "rating" và "review_count".

        Quá trình xử lý:
        1. Chuyển đổi dữ liệu đầu vào thành DataFrame.
        2. Trích xuất các đặc trưng quan trọng: "rating" và "review_count".
        3. Chuẩn hóa dữ liệu bằng StandardScaler.
        4. Sử dụng mô hình K-Means để phân cụm.
        5. Gán nhãn cụm (cluster) vào dữ liệu ban đầu.

        Tham số:
        -------
        data : dict hoặc list
            Dữ liệu đầu vào cần phân cụm, chứa ít nhất hai cột:
            - "rating": Điểm đánh giá.
            - "review_count": Số lượng đánh giá.

        Trả về:
        -------
        pandas.DataFrame
            DataFrame bao gồm dữ liệu gốc và cột "cluster" chứa nhãn cụm.
        """
        # Chuyển đổi dữ liệu sang DataFrame
        df = pd.DataFrame(data)

        # Trích xuất các đặc trưng (rating, review_count)
        features = df[["rating", "review_count"]]

        # Chuẩn hóa các đặc trưng
        features_scaled = self.scaler.fit_transform(features)

        # Phân cụm và gán nhãn
        df["cluster"] = self.model.fit_predict(features_scaled)
        return df
