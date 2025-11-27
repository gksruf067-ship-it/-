import tkinter as tk
from tkinter import ttk
import winsound # 윈도우 기본 소리를 위한 모듈
from control_panel import ControlPanel

class ElevatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("엘리베이터 시뮬레이션")
        self.root.geometry("350x750") # 윈도우 크기 고정 (외부 버튼 공간 확보)

        # --- 상수 정의 ---
        self.NUM_FLOORS = 7
        self.FLOOR_HEIGHT = 100
        self.ELEVATOR_WIDTH = 80
        self.SHAFT_WIDTH = 120
        self.CANVAS_HEIGHT = self.NUM_FLOORS * self.FLOOR_HEIGHT

        # --- 상태 변수 ---
        self.current_floor = 1
        self.is_busy = False # 이동, 문 개폐 등 엘리베이터가 동작 중인지 여부
        self.door_open = False
        self.auto_close_job = None # 자동 문닫힘 작업을 저장할 변수
        self.request_queue = [] # 층 요청을 저장할 큐
        self.external_buttons = {} # 외부 호출 버튼 위젯을 저장할 딕셔너리

        # --- GUI 구성 ---
        # 메인 프레임
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(expand=True, fill="both")

        # --- 제어판 생성 ---
        control_panel = ControlPanel(main_frame, self.NUM_FLOORS, self.request_floor, self.handle_open_button, self.handle_close_button)
        control_panel.pack(side="left", fill="y", padx=10)
        # 컨트롤 패널 인스턴스를 저장하여 상태를 업데이트할 수 있도록 함
        self.control_panel = control_panel


        # 엘리베이터 통로 (Canvas)
        shaft_frame = ttk.Frame(main_frame)
        shaft_frame.pack(side="left", fill="both", expand=True)
        
        self.canvas = tk.Canvas(shaft_frame, width=self.SHAFT_WIDTH + 40, height=self.CANVAS_HEIGHT, bg="lightgrey", highlightthickness=0)
        self.canvas.pack(pady=5)

        # 층 구분선 그리기
        for i in range(1, self.NUM_FLOORS):
            y = i * self.FLOOR_HEIGHT
            self.canvas.create_line(0, y, self.SHAFT_WIDTH, y, fill="darkgrey")

        # 외부 호출 버튼 생성
        for floor in range(1, self.NUM_FLOORS + 1):
            y_center = self.CANVAS_HEIGHT - (floor * self.FLOOR_HEIGHT) + (self.FLOOR_HEIGHT / 2)
            x_start = self.SHAFT_WIDTH + 10
            button_id = self.canvas.create_rectangle(x_start, y_center - 10, x_start + 20, y_center + 10, fill="lightgrey", outline="grey", width=2)
            self.canvas.tag_bind(button_id, '<Button-1>', lambda event, f=floor: self.handle_external_call(f))
            self.external_buttons[floor] = button_id


        # --- 엘리베이터 문 생성 ---
        elevator_y_start = self.CANVAS_HEIGHT - self.FLOOR_HEIGHT
        shaft_center_x = self.SHAFT_WIDTH / 2
        
        lx0 = (self.SHAFT_WIDTH - self.ELEVATOR_WIDTH) / 2
        lx1 = shaft_center_x
        ly0 = elevator_y_start
        ly1 = elevator_y_start + self.FLOOR_HEIGHT
        self.left_door = self.canvas.create_rectangle(lx0, ly0, lx1, ly1, fill="skyblue", outline="blue", width=2)
        
        rx0 = shaft_center_x
        rx1 = lx0 + self.ELEVATOR_WIDTH
        ry0 = ly0 # 오른쪽 문의 y 시작 좌표 추가
        self.right_door = self.canvas.create_rectangle(rx0, ry0, rx1, ly1, fill="skyblue", outline="blue", width=2)

    def request_floor(self, target_floor):
        """층 버튼 클릭 시 요청을 큐에 추가"""
        if target_floor not in self.request_queue:
            print(f"{target_floor}층 요청이 추가되었습니다.")
            self.request_queue.append(target_floor)
            self.process_next_request() # 새로운 요청이 들어오면 처리 시작
        else:
            print(f"이미 {target_floor}층 요청이 대기 중입니다.")

    def handle_external_call(self, floor):
        """외부 버튼 호출을 처리"""
        print(f"외부: {floor}층에서 호출이 있습니다.")
        self.canvas.itemconfig(self.external_buttons[floor], fill="orange") # 버튼 색상 변경
        self.request_floor(floor)

    def process_next_request(self):
        """요청 큐에서 다음 목적지를 처리"""
        if self.is_busy or not self.request_queue:
            return # 바쁘거나 처리할 요청이 없으면 반환

        target_floor = self.request_queue[0] # 큐에서 첫 번째 요청 확인

        # 현재 층에 대한 요청인 경우
        if target_floor == self.current_floor:
            if not self.door_open:
                self._open_door()
            else: # 이미 문이 열려있으면 요청을 제거하고 다음 요청 처리
                self.process_next_request()
            return

        # 다른 층으로 이동해야 할 경우
        if self.door_open:
            self._close_door(callback=lambda: self.process_next_request())
        else:
            self.is_busy = True
            self._move_animation(target_floor)

    def _calculate_y_for_floor(self, floor):
        return self.CANVAS_HEIGHT - (floor * self.FLOOR_HEIGHT)

    def _move_animation(self, target_floor):
        target_y = self._calculate_y_for_floor(target_floor)
        current_y = self.canvas.coords(self.left_door)[1]
        step = 1 if target_y > current_y else -1
        direction_symbol = '▼' if step > 0 else '▲'

        # 이동 시작음 재생 (낮은 '웅' 소리)
        winsound.Beep(300, 150)

        def _animate():
            y0 = self.canvas.coords(self.left_door)[1]

            # 현재 y좌표를 기반으로 실시간 층수 계산 (반올림하여 중간에 층이 바뀌도록)
            realtime_floor = round((self.CANVAS_HEIGHT - y0) / self.FLOOR_HEIGHT)

            # 이동 중에 상태 업데이트
            self.control_panel.update_status(realtime_floor, direction_symbol)

            if y0 == target_y:
                self.current_floor = target_floor
                # 도착음 재생 ('띵' 소리)
                winsound.Beep(1000, 200)
                self.control_panel.update_status(self.current_floor, "■") # 도착 표시
                print(f"{self.current_floor}층에 도착했습니다.")
                self._open_door() # 도착 후 문 열기
                return

            self.canvas.move(self.left_door, 0, step)
            self.canvas.move(self.right_door, 0, step)
            self.root.after(5, _animate)
        _animate()

    def _open_door(self, callback=None):
        self.door_open = True
        
        if self.auto_close_job:
            self.root.after_cancel(self.auto_close_job)
        print("문이 열립니다.")
        
        open_width = self.ELEVATOR_WIDTH * 0.8
        step = -1

        def _animate_open():
            self.is_busy = True # 문이 열리기 시작하면 바쁜 상태로 설정
            gap = self.canvas.coords(self.right_door)[0] - self.canvas.coords(self.left_door)[2]
            if gap >= open_width:
                self.canvas.itemconfig(self.external_buttons[self.current_floor], fill="lightgrey") # 외부 버튼 색상 복원
                self.request_queue.pop(0) # 문이 완전히 열리면 요청 제거
                print("문이 완전히 열렸습니다.")
                self.is_busy = False # 문이 다 열리면 바쁜 상태 해제
                self.auto_close_job = self.root.after(5000, self._close_door) # 자동 닫힘 시간을 5초로 변경
                if callback:
                    callback()
                return

            self.canvas.move(self.left_door, step, 0)
            self.canvas.move(self.right_door, -step, 0)
            self.root.after(15, _animate_open)
        _animate_open()

    def _close_door(self, callback=None):
        if not self.door_open: 
            if callback: callback()
            return
            
        if self.auto_close_job:
            self.root.after_cancel(self.auto_close_job)
            self.auto_close_job = None
        print("문이 닫힙니다.")
        
        step = 1
        def _animate_close():
            self.is_busy = True # 문이 닫히기 시작하면 바쁜 상태로 설정
            if self.canvas.coords(self.left_door)[2] >= self.SHAFT_WIDTH / 2:
                self.door_open = False
                self.is_busy = False
                print("문이 닫혔습니다.")
                if callback:
                    callback()
                else:
                    self.process_next_request() # 문 닫고 다음 요청 처리
                return
            
            self.canvas.move(self.left_door, step, 0)
            self.canvas.move(self.right_door, -step, 0)
            self.root.after(15, _animate_close)
        _animate_close()

    def handle_open_button(self):
        # 문이 열려있고 바쁘지 않은 상태(정지 상태)일 때
        if self.door_open and not self.is_busy:
            print("문 열림 시간을 연장합니다 (5초).")
            # 기존 자동 닫힘 타이머 취소
            if self.auto_close_job: self.root.after_cancel(self.auto_close_job)
            # 5초 뒤에 문이 닫히도록 새로운 타이머 설정
            self.auto_close_job = self.root.after(5000, self._close_door)
        # 엘리베이터가 움직이는 중일 때
        elif self.is_busy and not self.door_open:
            print("이동 중에는 문을 조작할 수 없습니다.")
        # 그 외의 경우 (문이 닫혀있을 때) 문을 열고 5초 타이머 시작
        else:
            self._open_door()

    def handle_close_button(self):
        if not self.door_open:
            print("문이 이미 닫혀있습니다.")
            return
        self._close_door()

if __name__ == "__main__":
    root = tk.Tk()
    app = ElevatorApp(root)
    root.mainloop()
