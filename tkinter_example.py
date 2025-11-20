import tkinter as tk
from tkinter import ttk

class ElevatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("엘리베이터 시뮬레이션")
        self.root.geometry("280x750") # 윈도우 크기 고정 (7층에 맞게 조정)

        # --- 상수 정의 ---
        self.NUM_FLOORS = 7
        self.FLOOR_HEIGHT = 100
        self.ELEVATOR_WIDTH = 80
        self.SHAFT_WIDTH = 120
        self.CANVAS_HEIGHT = self.NUM_FLOORS * self.FLOOR_HEIGHT

        # --- 상태 변수 ---
        self.current_floor = 1
        self.is_moving = False

        # --- GUI 구성 ---
        # 메인 프레임
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(expand=True, fill="both")

        # --- 제어판 (버튼) ---
        control_panel = ttk.Frame(main_frame)
        control_panel.pack(side="left", fill="y", padx=10)
        ttk.Label(control_panel, text="층 선택", font=("Arial", 14)).pack(pady=10)

        # 층 버튼 생성
        for floor in range(self.NUM_FLOORS, 0, -1):
            button = ttk.Button(control_panel, text=f"{floor}층", command=lambda f=floor: self.request_floor(f))
            button.pack(pady=5, fill='x')

        # 엘리베이터 통로 (Canvas)
        shaft_frame = ttk.Frame(main_frame)
        shaft_frame.pack(side="left", fill="both", expand=True)
        
        self.canvas = tk.Canvas(shaft_frame, width=self.SHAFT_WIDTH, height=self.CANVAS_HEIGHT, bg="lightgrey", highlightthickness=0)
        self.canvas.pack(pady=5)

        # 층 구분선 그리기
        for i in range(1, self.NUM_FLOORS):
            y = i * self.FLOOR_HEIGHT
            self.canvas.create_line(0, y, self.SHAFT_WIDTH, y, fill="darkgrey")

        # --- 엘리베이터 문 생성 ---
        # 엘리베이터의 초기 y 위치 (1층)
        elevator_y_start = self.CANVAS_HEIGHT - self.FLOOR_HEIGHT
        
        # 통로 중앙 x 좌표
        shaft_center_x = self.SHAFT_WIDTH / 2
        
        # 왼쪽 문 (사각형)
        lx0 = (self.SHAFT_WIDTH - self.ELEVATOR_WIDTH) / 2
        ly0 = elevator_y_start
        lx1 = shaft_center_x
        ly1 = self.CANVAS_HEIGHT
        self.left_door = self.canvas.create_rectangle(lx0, ly0, lx1, ly1, fill="skyblue", outline="blue", width=2)
        
        # 오른쪽 문 (사각형)
        rx0 = shaft_center_x
        ry0 = elevator_y_start
        rx1 = lx0 + self.ELEVATOR_WIDTH
        ry1 = self.CANVAS_HEIGHT
        self.right_door = self.canvas.create_rectangle(rx0, ry0, rx1, ry1, fill="skyblue", outline="blue", width=2)

    def request_floor(self, target_floor):
        """층 버튼 클릭 시 호출되어 이동을 시작시키는 함수"""
        if self.is_moving:
            print("엘리베이터가 이미 이동 중입니다.")
            return
        if target_floor == self.current_floor:
            print(f"이미 {self.current_floor}층에 있습니다.")
            return

        print(f"{target_floor}층으로 이동을 시작합니다.")
        self.is_moving = True
        self._move_animation(target_floor)

    def _calculate_y_for_floor(self, floor):
        """층 번호에 해당하는 canvas의 y좌표(상단 기준)를 계산"""
        return self.CANVAS_HEIGHT - (floor * self.FLOOR_HEIGHT)

    def _move_animation(self, target_floor):
        """엘리베이터를 부드럽게 이동시키는 애니메이션"""
        target_y = self._calculate_y_for_floor(target_floor)
        current_y = self.canvas.coords(self.left_door)[1]

        # 이동 방향 결정 (1: 하강, -1: 상승)
        step = 1 if target_y > current_y else -1

        def _animate():
            y0 = self.canvas.coords(self.left_door)[1]

            if y0 == target_y:
                self.current_floor = target_floor
                self.is_moving = False
                print(f"{self.current_floor}층에 도착했습니다.")
                return

            # 양쪽 문을 함께 이동
            self.canvas.move(self.left_door, 0, step)
            self.canvas.move(self.right_door, 0, step)

            # 10ms 후에 다음 프레임 실행
            self.root.after(10, _animate)

        _animate()

# --- 프로그램 실행 ---
if __name__ == "__main__":
    # Tkinter 루트 윈도우 생성
    root = tk.Tk()
    
    # 앱 인스턴스 생성
    app = ElevatorApp(root)
    
    # 이벤트 루프 시작
    root.mainloop()
