import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.patches import Patch
import mplcursors
import numpy as np
from DataGenerator import *
from Clustering import *

# App: Xây dựng giao diện ứng dụng
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Phân Cụm Sản Phẩm")
        self.root.geometry("1400x800")  
        self.root.minsize(800, 600)  # Đặt kích thước tối thiểu
        self.root.resizable(True, True)  # Cho phép thay đổi kích thước

        # Căn giữa màn hình khi khởi động
        self.center_window(1400, 800)

        self.data_generator = DataGenerator()
        self.canvas = None
        self.clustering = None
        self.data = None
        self.sort_column = None
        self.sort_reverse = False

        # Cấu hình style chuyên nghiệp hơn
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Thay đổi theme cho hiện đại
        self.style.configure("TButton", font=("Inter", 10, "bold"), padding=8, background="#007acc", foreground="white")
        self.style.map("TButton", background=[("active", "#005c99")])
        self.style.configure("TLabel", font=("Inter", 10))
        self.style.configure("TTreeview", font=("Inter", 10))
        self.style.configure("TEntry", font=("Inter", 10))
        self.style.configure("TScrollbar", background="#cccccc")

        self.setup_ui()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_left = int(screen_width / 2 - width / 2)
        self.root.geometry(f'{width}x{height}+{position_left}+{position_top}')

    def setup_ui(self):
        # Thanh điều hướng (Menu bar)
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Lưu dữ liệu CSV", command=self.save_file)
        file_menu.add_command(label="Tải dữ liệu CSV", command=self.load_file)
        file_menu.add_command(label="Reset", command=self.reset_screen)

        # Thanh trạng thái
        self.status_bar = ttk.Label(
            self.root, text="Chào mừng bạn đến với Phân Cụm Sản Phẩm!",
            relief=tk.SUNKEN, anchor=tk.W, background="#f0f4f8", padding=(10, 5)
        )
        self.status_bar.pack(side=tk.TOP, fill=tk.X)

        # Khung chức năng chính
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.pack(fill=tk.X, padx=20, pady=10)

        # Sử dụng grid layout thay vì pack để dễ quản lý vị trí
        btn_random_100 = ttk.Button(action_frame, text="Random 100 sản phẩm", command=self.random_100)
        btn_random_100.grid(row=0, column=0, padx=10, pady=5)

        btn_random_10 = ttk.Button(action_frame, text="Random 10 sản phẩm", command=self.random_10)
        btn_random_10.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(action_frame, text="Số cụm:").grid(row=0, column=2, padx=10)
        self.cluster_entry = ttk.Entry(action_frame, width=10)
        self.cluster_entry.grid(row=0, column=3, padx=10)

        btn_cluster = ttk.Button(action_frame, text="Phân cụm", command=self.cluster_data)
        btn_cluster.grid(row=0, column=4, padx=10, pady=5)

        best_cluster_button = ttk.Button(action_frame, text="Sản phẩm tốt nhất", command=lambda: self.show_best_cluster(pd.DataFrame(self.data)))
        best_cluster_button.grid(row=0, column=5, padx=10, pady=5)

        compare_button = ttk.Button(action_frame, text="So sánh cụm", command=lambda: self.compare_clusters(pd.DataFrame(self.data)))
        compare_button.grid(row=0, column=6, padx=10, pady=5)

        button_elbow = ttk.Button(action_frame, text="Elbow Method", command=lambda: self.elbow_method(pd.DataFrame(self.data)))
        button_elbow.grid(row=0, column=7, padx=10, pady=5)

        btn_save_result = ttk.Button(action_frame, text="Lưu kết quả CSV", command=self.save_result)
        btn_save_result.grid(row=0, column=8, padx=10, pady=5)

        # Bảng hiển thị dữ liệu
        columns = ["id", "name", "category", "brand", "rating", "review_count", "cluster", "quality"]
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", yscrollcommand=self.tree_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, anchor=tk.CENTER, width=120)

    def random_100(self):
        self.data = self.data_generator.random_product(100)
        self.display_data(self.data)
        self.update_status("Dữ liệu ngẫu nhiên 100 sản phẩm đã được tạo.")

    def random_10(self):
        self.data = self.data_generator.random_product(10)
        self.display_data(self.data)
        self.update_status("Dữ liệu ngẫu nhiên 10 sản phẩm đã được tạo.")

    def save_file(self):
        if not self.data:
            messagebox.showwarning("Lỗi", "Chưa có dữ liệu để lưu!")
            return
        
        # Mở cửa sổ lưu file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        
        if file_path:
            try:
                # Chuyển dữ liệu sang DataFrame
                df = pd.DataFrame(self.data)
                # Lưu DataFrame vào file CSV
                df.to_csv(file_path, index=False)
                self.update_status(f"Dữ liệu đã được lưu tại {file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")

    def load_file(self):
        # Mở cửa sổ chọn file
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        
        if file_path:
            try:
                # Đọc dữ liệu từ file CSV vào DataFrame
                df = pd.read_csv(file_path)
                # Chuyển đổi lại dữ liệu thành dạng list of dictionaries
                self.data = df.to_dict("records")
                self.display_data(self.data)
                self.update_status(f"Dữ liệu đã được tải từ {file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở file: {str(e)}")

    def save_result(self):
        if not self.data:
            messagebox.showwarning("Lỗi", "Chưa có dữ liệu để lưu!")
            return
        
        # Lưu kết quả phân cụm vào file CSV
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        
        if file_path:
            try:
                # Chuyển đổi dữ liệu thành DataFrame
                df = pd.DataFrame(self.data)
                # Lưu DataFrame vào file CSV
                df.to_csv(file_path, index=False)
                self.update_status(f"Dữ liệu phân cụm đã được lưu tại {file_path}")
                
                # Lưu biểu đồ phân cụm dưới dạng hình ảnh (SVG, PNG, v.v.)
                chart_file_path = file_path.replace(".csv", ".png")  # Lưu với định dạng hình ảnh
                fig, ax = plt.subplots(figsize=(8, 6))
                
                scatter = ax.scatter(
                    df["rating"], 
                    df["review_count"], 
                    c=df["cluster"], 
                    cmap="viridis", 
                    s=50, 
                    alpha=0.7, 
                    edgecolor="k"
                )
                
                ax.set_xlabel("Đánh giá trung bình")
                ax.set_ylabel("Số lượng đánh giá")
                ax.set_title("Biểu đồ phân cụm sản phẩm")
                
                # Lưu biểu đồ
                fig.savefig(chart_file_path)
                plt.close(fig)
                self.update_status(f"Biểu đồ phân cụm đã được lưu tại {chart_file_path}")
            
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu kết quả: {str(e)}")

    def preprocess_data(self):
        if not self.data:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu để xử lý!")
            return None

        # Chuyển đổi dữ liệu sang DataFrame
        df = pd.DataFrame(self.data)
        
        # Loại bỏ các hàng có giá trị thiếu
        initial_len = len(df)
        df = df.dropna()
        removed_rows = initial_len - len(df)

        # Kiểm tra và cảnh báo nếu có giá trị bị loại bỏ
        if removed_rows > 0:
            messagebox.showinfo("Thông báo", f"Đã loại bỏ {removed_rows} dòng dữ liệu thiếu!")

        # Chuyển đổi các cột không phải số (nếu cần)
        numeric_columns = ["rating", "review_count"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Loại bỏ giá trị không hợp lệ (vd: NaN sau chuyển đổi)
        df = df.dropna(subset=numeric_columns)

        # Cập nhật lại dữ liệu sau khi xử lý
        self.data = df.to_dict("records")
        return df

    def cluster_data(self):
        if not self.data:
            messagebox.showerror("Lỗi", "Chưa có dữ liệu để phân cụm!")
            return

        # Gọi hàm tiền xử lý
        df = self.preprocess_data()
        if df is None or df.empty:
            messagebox.showerror("Lỗi", "Không đủ dữ liệu hợp lệ để phân cụm!")
            return

        try:
            # Lấy số cụm từ người dùng
            n_clusters = int(self.cluster_entry.get())
            if n_clusters < 1:
                raise ValueError("Số cụm phải lớn hơn 0.")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số cụm hợp lệ.")
            return
        
        # Khởi tạo Clustering và phân cụm
        self.clustering = Clustering(n_clusters=n_clusters)
        df = self.clustering.fit_predict(self.data)
        
        # Thêm cột đánh giá chất lượng
        df["quality"] = df["rating"].apply(
            lambda x: "Tốt" if x > 4 else ("Trung bình" if 3 <= x <= 4 else "Kém")
        )
        
        # Xác định cụm tốt nhất
        cluster_stats = df.groupby("cluster").agg(
            avg_rating=("rating", "mean"),
            total_reviews=("review_count", "sum")
        ).reset_index()
        
        # Lọc ra cụm tốt nhất (cụm có rating trung bình cao nhất và thuộc nhóm "Tốt")
        good_clusters = cluster_stats[cluster_stats["avg_rating"] > 4]
        if not good_clusters.empty:
            best_cluster = good_clusters.loc[good_clusters["avg_rating"].idxmax()]
            best_cluster_id = int(best_cluster["cluster"])
            avg_rating = best_cluster["avg_rating"]
            total_reviews = best_cluster["total_reviews"]
            
            # Cập nhật status bar với thông tin cụm tốt nhất
            self.update_status(
                f"Gợi ý sản phẩm từ cụm tốt nhất (Cụm {best_cluster_id}): "
                f"Rating trung bình = {avg_rating:.2f}, Tổng số đánh giá = {total_reviews}."
            )
        else:
            # Trường hợp không có cụm "Tốt"
            self.update_status("Không có cụm nào thuộc nhóm 'Tốt'.")
        
        # Cập nhật dữ liệu với nhãn cụm và chất lượng
        self.data = df.to_dict("records")
        self.display_data(self.data)
        self.display_clusters(df)

    def display_data(self, data):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in data:
            self.tree.insert("", "end", values=list(row.values()))

    def display_clusters(self, df):
        # Xóa biểu đồ cũ (nếu có)
        for widget in self.tree_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        # Hiển thị biểu đồ phân cụm
        fig, ax = plt.subplots(figsize=(8, 6))  # Tăng kích thước biểu đồ

        # Scatter plot các điểm dữ liệu
        scatter = ax.scatter(
            df["rating"], 
            df["review_count"], 
            c=df["cluster"], 
            cmap="viridis", 
            s=50, 
            alpha=0.7,  # Độ trong suốt
            edgecolor="k"  # Viền đen
        )
        
        # Hiển thị trung tâm cụm (Centroids)
        if self.clustering and self.clustering.model.cluster_centers_ is not None:
            centroids = self.clustering.model.cluster_centers_
            centroids_original = self.clustering.scaler.inverse_transform(centroids)  # Chuyển về giá trị gốc
            
            # Vẽ các điểm centroid
            ax.scatter(
                centroids_original[:, 0],  # Rating
                centroids_original[:, 1],  # Review count
                c="red",  # Màu đỏ
                s=200,  # Kích thước lớn hơn
                marker="X",  # Biểu tượng là chữ X
                label="Centroid"  # Gắn nhãn
            )

        # Gắn nhãn cho trục
        ax.set_xlabel("Đánh giá trung bình")
        ax.set_ylabel("Số lượng đánh giá")
        ax.set_title("Biểu đồ phân cụm sản phẩm")

        # Tạo chú thích (legend)
        clusters = df["cluster"].unique()
        legend_labels = [Patch(color=scatter.cmap(scatter.norm(c)), label=f"Cụm {int(c)}") for c in clusters]
        ax.legend(
            handles=legend_labels + [Patch(color="red", label="Centroid")], 
            title="Chú thích", 
            bbox_to_anchor=(1.05, 1),  # Đặt chú thích bên ngoài biểu đồ
            loc="upper left", 
            borderaxespad=0
        )

        # Điều chỉnh khoảng cách để không gian biểu đồ và chú thích không bị chèn lên nhau
        fig.subplots_adjust(right=0.8)

        # Thêm tooltip bằng mplcursors
        cursor = mplcursors.cursor(scatter, hover=True)
        cursor.connect(
            "add", 
            lambda sel: sel.annotation.set_text(
                f"Rating: {sel.target[0]:.2f}\nReviews: {int(sel.target[1])}"
            )
        )

        # Hiển thị biểu đồ trên giao diện Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.tree_frame)
        canvas.get_tk_widget().pack(pady=10)
        canvas.draw()

    def get_best_cluster(self, df):
        # Tính toán rating trung bình cho mỗi cụm
        cluster_means = df.groupby("cluster")["rating"].mean()
        best_cluster = cluster_means.idxmax()  # Cụm có rating trung bình cao nhất

        # Lọc các sản phẩm trong cụm tốt nhất
        best_cluster_products = df[df["cluster"] == best_cluster]

        # Tính toán giá trị trung bình của rating và review_count trong cụm
        C = best_cluster_products["rating"].mean()  # Đánh giá trung bình của cụm
        m = best_cluster_products["review_count"].quantile(0.75)  # Ngưỡng 75% cho số lượng đánh giá

        # Lọc các sản phẩm đủ điều kiện theo review_count
        qualified_products = best_cluster_products[best_cluster_products["review_count"] >= m]

        if qualified_products.empty:
            # Nếu không có sản phẩm đủ điều kiện, chọn sản phẩm có rating cao nhất
            best_product = best_cluster_products.sort_values(by="rating", ascending=False).iloc[0]
        else:
            # Tính toán Weighted Rating (WR) cho mỗi sản phẩm đủ điều kiện
            qualified_products["weighted_rating"] = qualified_products.apply(
                lambda x: (x["review_count"] / (x["review_count"] + m)) * x["rating"] +
                        (m / (x["review_count"] + m)) * C, axis=1
            )

            # Chọn sản phẩm có Weighted Rating cao nhất
            best_product = qualified_products.sort_values(by="weighted_rating", ascending=False).iloc[0]

        return best_cluster, best_product

    def show_best_cluster(self, df):
        best_cluster, best_product = self.get_best_cluster(df)
        
        # Hiển thị thông tin cụm tốt nhất và sản phẩm tốt nhất
        info = f"""Cụm tốt nhất: {best_cluster}
    Sản phẩm tốt nhất trong cụm:
    - Tên sản phẩm: {best_product['name']}
    - Đánh giá: {best_product['rating']}
    - Số lượng đánh giá: {best_product['review_count']}
    """
        messagebox.showinfo("Cụm tốt nhất", info)

    def compare_clusters(self, df):
        # Kiểm tra dữ liệu đầu vào
        if "cluster" not in df.columns or "rating" not in df.columns or "review_count" not in df.columns:
            messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ để so sánh cụm. Vui lòng phân cụm trước!")
            return

        if df.empty:
            messagebox.showerror("Lỗi", "Dữ liệu trống, không thể so sánh giữa các cụm!")
            return

        # Tính trung bình rating và review_count cho từng cụm
        cluster_summary = df.groupby("cluster").agg(
            avg_rating=("rating", "mean"),
            avg_review_count=("review_count", "mean"),
            product_count=("name", "count")
        ).reset_index()

        # Xóa biểu đồ cũ (nếu có)
        for widget in self.tree_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        # Hiển thị kết quả
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Vẽ avg_rating trên trục y chính
        x = cluster_summary["cluster"]
        bar_width = 0.4
        bars1 = ax1.bar(x - bar_width / 2, cluster_summary["avg_rating"], bar_width, label="Rating trung bình", color="blue")
        ax1.set_ylabel("Rating trung bình (1-5)", color="blue")
        ax1.set_xlabel("Cụm")
        ax1.tick_params(axis="y", labelcolor="blue")
        ax1.set_title("So sánh giữa các cụm")

        # Thêm số liệu vào mỗi cột trên trục y chính
        for bar in bars1:
            yval = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,  # X vị trí
                yval,  # Y vị trí
                f'{yval:.2f}',  # Giá trị hiển thị
                ha='center',  # Căn giữa
                va='bottom',  # Căn dưới để số liệu không bị tràn lên
                color='blue',  # Màu chữ
                fontweight='bold'  # Màu chữ đậm
            )

        # Tạo trục y phụ cho avg_review_count
        ax2 = ax1.twinx()
        bars2 = ax2.bar(x + bar_width / 2, cluster_summary["avg_review_count"], bar_width, label="Review trung bình", color="orange")
        ax2.set_ylabel("Review trung bình", color="orange")
        ax2.tick_params(axis="y", labelcolor="orange")

        # Thêm số liệu vào mỗi cột trên trục y phụ
        for bar in bars2:
            yval = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,  # X vị trí
                yval,  # Y vị trí
                f'{yval:.0f}',  # Giá trị hiển thị (làm tròn thành số nguyên)
                ha='center',  # Căn giữa
                va='bottom',  # Căn dưới
                color='orange',  # Màu chữ
                fontweight='bold'  # Màu chữ đậm
            )

        # Thêm chú thích
        fig.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)

        # Hiển thị biểu đồ trên Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.tree_frame)
        canvas.get_tk_widget().pack(pady=10)
        canvas.draw()

    def elbow_method(self, df):
        # Kiểm tra dữ liệu đầu vào
        if "rating" not in df.columns or "review_count" not in df.columns:
            messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ để sử dụng Elbow Method. Hãy kiểm tra dữ liệu đầu vào!")
            return

        if df.empty:
            messagebox.showerror("Lỗi", "Dữ liệu trống, không thể thực hiện Elbow Method!")
            return

        # Chuẩn bị dữ liệu
        features = df[["rating", "review_count"]]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        # Chạy KMeans với các số cụm khác nhau
        sse = []
        k_range = range(1, 11)  # Thử từ 1 đến 10 cụm
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(scaled_features)
            sse.append(kmeans.inertia_)  # inertia_ là SSE của mô hình

        # Tự động tìm điểm Elbow bằng phương pháp góc lớn nhất
        def find_elbow_point(sse, k_range):
            diffs = np.diff(sse)  # Sự chênh lệch SSE giữa các cụm k
            curvature = np.diff(diffs)  # Đạo hàm bậc hai để đo độ cong
            elbow_point = np.argmax(curvature) + 2  # Điểm tối ưu thường là nơi độ cong lớn nhất
            return elbow_point

        optimal_k = find_elbow_point(sse, k_range)

        # Xóa biểu đồ cũ (nếu có)
        for widget in self.tree_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        # Vẽ biểu đồ Elbow
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(k_range, sse, marker="o", linestyle="--", color="b", label="SSE")
        ax.axvline(optimal_k, color="r", linestyle="--", label=f"Elbow: k={optimal_k}")
        ax.set_xlabel("Số cụm (k)")
        ax.set_ylabel("SSE")
        ax.set_title("Elbow Method - Tìm số cụm tối ưu")
        ax.legend()
        ax.grid(True)

        # Hiển thị biểu đồ trên Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.tree_frame)
        canvas.get_tk_widget().pack(pady=10)
        canvas.draw()

        # Gợi ý cho người dùng
        messagebox.showinfo("Gợi ý", f"Số cụm tối ưu được gợi ý là {optimal_k}. Bạn có thể chọn số cụm này để phân cụm sản phẩm!")

    def update_status(self, message):
        self.status_bar.config(text=message)

    def reset_screen(self):
        # Xóa dữ liệu và các phần hiển thị
        self.data = None
        self.clustering = None
        self.cluster_entry.delete(0, tk.END)  # Xóa nhập liệu số cụm
        self.update_status("Màn hình đã được làm mới.")
        
        # Xóa tất cả các dòng trong Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Xóa tất cả các biểu đồ cũ (nếu có)
        for widget in self.tree_frame.winfo_children():
            if isinstance(widget, tk.Canvas):  # Kiểm tra nếu widget là Canvas
                widget.destroy()  # Xóa biểu đồ cũ

    def sort_by_column(self, column):
        if not self.data:
            return

        # Xác định cách sắp xếp theo từng cột
        if column not in ["cluster", "rating", "review_count"]:
            return  # Nếu cột không phải là cluster, rating, review_count thì không làm gì

        # Đổi chiều sắp xếp (tăng dần <-> giảm dần)
        self.sort_reverse = (self.sort_column == column and not self.sort_reverse)  # Đổi chiều sắp xếp
        self.sort_column = column

        # Sắp xếp dữ liệu theo cột và chiều sắp xếp
        if column == "cluster":
            self.data = sorted(self.data, key=lambda x: x[column], reverse=self.sort_reverse)
        else:
            # Đảm bảo giá trị số của cột rating và review_count
            self.data = sorted(self.data, key=lambda x: float(x[column]), reverse=self.sort_reverse)

        # Hiển thị lại dữ liệu sau khi sắp xếp
        self.display_data(self.data)

# Khởi chạy ứng dụng
root = tk.Tk()
app = App(root)
root.mainloop()