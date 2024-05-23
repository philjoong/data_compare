from P4 import P4, P4Exception
import os
os.environ['P4CHARSET'] = 'utf8'
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from babel.numbers import *
from tkinter import messagebox
from tkinter import Toplevel, Text, Scrollbar, END
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import pandas as pd
import io
import numpy as np

class DateTimePickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STREAM 비교")

        # 시작 날짜 선택기
        self.start_cal_label = ttk.Label(root, text="시작 날짜 선택:")
        self.start_cal_label.grid(row=0, column=0, padx=10, pady=10)
        self.start_cal = Calendar(root, selectmode='day')
        self.start_cal.grid(row=0, column=1, padx=10, pady=10)

        # 시작 시간 선택기
        self.start_time_label = ttk.Label(root, text="시작 시간 선택:")
        self.start_time_label.grid(row=1, column=0, padx=10, pady=10)
        self.start_hour = ttk.Combobox(root, values=[f"{i:02d}" for i in range(24)], width=5)
        self.start_hour.grid(row=1, column=1, padx=10, pady=10, sticky="W")
        self.start_minute = ttk.Combobox(root, values=[f"{i:02d}" for i in range(60)], width=5)
        self.start_minute.grid(row=1, column=1, padx=50, pady=10)  # 위치 조정을 위한 padx 값 변경
        self.start_minute.set("00")  # 분 선택기의 기본값 설정

        # 종료 날짜 선택기
        self.end_cal_label = ttk.Label(root, text="종료 날짜 선택:")
        self.end_cal_label.grid(row=2, column=0, padx=10, pady=10)
        self.end_cal = Calendar(root, selectmode='day')
        self.end_cal.grid(row=2, column=1, padx=10, pady=10)

        # 종료 시간 선택기
        self.end_time_label = ttk.Label(root, text="종료 시간 선택:")
        self.end_time_label.grid(row=3, column=0, padx=10, pady=10)
        self.end_hour = ttk.Combobox(root, values=[f"{i:02d}" for i in range(24)], width=5)
        self.end_hour.grid(row=3, column=1, padx=10, pady=10, sticky="W")
        self.end_minute = ttk.Combobox(root, values=[f"{i:02d}" for i in range(60)], width=5)
        self.end_minute.grid(row=3, column=1, padx=50, pady=10)  # 위치 조정을 위한 padx 값 변경
        self.end_minute.set("00")  # 분 선택기의 기본값 설정

        # 확인 범위 선택
        self.type_label = ttk.Label(root, text="루트 폴더 선택:")
        self.type_label.grid(row=4, column=0, padx=10, pady=10)  # 여기를 row=4로 조정했습니다.

        # "typeA"와 "typeB" 중에서 선택할 수 있는 Combobox 생성
        self.type_combobox = ttk.Combobox(root, values=[# 파일 경로 들어가 있어 제거함], width=30)
        self.type_combobox.grid(row=4, column=1, padx=10, pady=10, sticky="W")

        # 비밀번호 입력
        self.password_label = ttk.Label(root, text="비밀번호 입력:")
        self.password_label.grid(row=5, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(root, show="*")
        self.password_entry.grid(row=5, column=1, padx=10, pady=10, sticky="W")

        # 확인 버튼
        self.confirm_button = ttk.Button(root, text="확인", command=self.show_selected_times)
        self.confirm_button.grid(row=6, column=0, columnspan=2, pady=20)

    def xml_to_df(self, xml_content, start_row=0, max_rows=None):
        """
        Parse XML content to a pandas DataFrame.
        Adjust this function to match the structure of your specific XML file.
        """
        # Parse XML
        context = ET.iterparse(io.StringIO(xml_content), events=("start", "end"))
        context = iter(context)
        event, root = next(context)
        data = []
        current_row = 0
        total_rows = 0
        namespaces = {}
        for event, elem in context:
            if event == 'start' and '}' in elem.tag:
                ns = elem.tag.strip().split('}')[0].strip('{')
                if ns:
                    namespaces['ns'] = ns

            if event == 'end' and elem.tag.endswith('row'):
                if current_row >= start_row:
                    row_data = []
                    for cell in elem.findall('.//ns:c', namespaces):
                        value = cell.find('.//ns:v', namespaces)
                        row_data.append(value.text if value is not None else None)
                    data.append(row_data)
                    total_rows += 1
                    if max_rows and total_rows >= max_rows:
                        break
                current_row += 1
                root.clear()

        return pd.DataFrame(data)

    def create_popup(self, title, text):
        popup = Toplevel()
        popup.title(title)
        popup.geometry("800x600")
        # Text 위젯과 Scrollbar 생성
        txt = Text(popup, wrap="word", height=10, width=50)
        scroll_bar = Scrollbar(popup, command=txt.yview)
        txt.config(yscrollcommand=scroll_bar.set)

        # Scrollbar를 Text 위젯에 연결
        txt.grid(row=0, column=0, sticky="nsew")
        scroll_bar.grid(row=0, column=1, sticky="ns")

        # 팝업 창 크기 조절을 위한 Weight 설정
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)

        # 전달받은 텍스트를 Text 위젯에 추가
        txt.insert(END, text)

        # 사용자가 텍스트를 수정하지 못하게 함
        txt.config(state="disabled")

    def compare_split_dataframes(self, 1_splits, 2_splits):
        diff_1_list = []
        diff_2_list = []

        for 1_part, 2_part in zip(1_splits, 2_splits):
            diff_1 = pd.concat([1_part, 2_part]).drop_duplicates(keep=False)
            diff_2 = pd.concat([2_part, 1_part]).drop_duplicates(keep=False)

            if not diff_1.empty:
                diff_1_list.append(diff_1)
            if not diff_2.empty:
                diff_2_list.append(diff_2)

        return diff_1_list, diff_2_list

    def _compare(self, 1_content, 2_content):
        if 1_content == 2_content:
            # 두 내용이 같다면 빈 리스트 반환
            return [], []

    def extract_and_compare_excel(self, zip1, zip2):
        diff_1_list = []
        diff_2_list = []
        with ZipFile(io.BytesIO(zip1)) as zip_file_1, ZipFile(io.BytesIO(zip2)) as zip_file_2:
            xml_files_1 = [f for f in zip_file_1.namelist() if f.endswith('.xml') and 'sheet1' in f]
            xml_files_2 = [f for f in zip_file_2.namelist() if f.endswith('.xml') and 'sheet1' in f]

            if not xml_files_1 or not xml_files_2:
                print("No XML file found.")
                return None

            with zip_file_1.open(xml_files_1[0]) as _file_1, zip_file_2.open(xml_files_2[0]) as _file_2:
                xml_content_1 = _file_1.read().decode('utf-8')
                xml_content_2 = _file_2.read().decode('utf-8')
                _row = 0
                while _row < 500000:
                    _end = _row + 1000

                    df_1 = self.xml_to_df(xml_content_1, _row, _end)
                    df_2 = self.xml_to_df(xml_content_2, _row, _end)

                    if df_1.empty and df_2.empty:
                        break
                    # 데이터프레임을 청크 사이즈에 따라 나누기
                    diff_tw = pd.concat([df_1, df_2]).drop_duplicates(keep=False)
                    diff_jp = pd.concat([df_2, df_1]).drop_duplicates(keep=False)

                    if not diff_tw.empty:
                        diff_tw_list.append(diff_tw)
                    if not diff_jp.empty:
                        diff_jp_list.append(diff_jp)
                    _row = _row + 1001
                return diff_tw_list, diff_jp_list

    def show_selected_times(self):
        local_folder_path = "./byProductPoll"
        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)
        password = self.password_entry.get()
        type = self.type_combobox.get()
        folder_path_1 = ""
        folder_path_2 = ""
        if type =="" # 경로 파일 제거함
            folder_path_1 = "" # 경로 파일 제거함
            folder_path_2 = "" # 경로 파일 제거함
        elif type == "" # 경로 파일 제거함
            folder_path_1 = "" # 경로 파일 제거함
            folder_path_2 = "" # 경로 파일 제거함

        start_date_str = self.start_cal.get_date().split('/')  # 시작 날짜 문자열
        start_datetime = datetime.datetime.now().replace(year=int("20"+start_date_str[2]), month=int(start_date_str[0]), day=int(start_date_str[1]), hour=int(self.start_hour.get()), minute=int(self.start_minute.get()), second=0, microsecond=0).strftime('%Y/%m/%d:%H:%M:%S')
        end_date_str = self.end_cal.get_date().split('/')  # 종료 날짜 문자열
        end_datetime = datetime.datetime.now().replace(year=int("20"+end_date_str[2]), month=int(end_date_str[0]), day=int(end_date_str[1]), hour=int(self.end_hour.get()), minute=int(self.end_minute.get()), second=0, microsecond=0).strftime('%Y/%m/%d:%H:%M:%S')
        # messagebox.showinfo("정보", f"시작 시간: {start_datetime}\n종료 시간: {end_datetime}\n비밀번호: {password}")

        p4 = P4()
        p4.port = "" # 경로 파일 제거함
        p4.user = "" # 경로 파일 제거함
        try:
            p4.connect()
            # password = getpass.getpass("Enter the password: ")
            p4.run_login(password=password)

            # 지정된 경로 내의 최근 일주일간 변경된 changelists 조회
            changes_1 = p4.run("files", f"{folder_path_1}@{start_datetime},{end_datetime}")
            # today_str = datetime.date.today().strftime('%Y/%m/%d')
            # changes_1 = p4.run_changes("-s", "submitted", f"@{today_str},@now", folder_path_1_release)
            # _changes_1 = p4.run_changes("-m10", f"@{today_str}", folder_path_1_release)
            # changes_1 = p4.run_changes("-m50", f"{folder_path_1_release}@{one_week_ago}")

            # 변경된 파일명을 저장할 리스트
            changed_files_1 = set()
            diff_file_set_1 = set()
            desc_lists_1 = []

            for change in changes_1:
                _filename = change['depotFile']
                if (folder_path_tw.replace("...", "")) in _filename:
                    temp_str = _filename
                    if "String" not in temp_str:
                        diff_file_set_1.add(temp_str)
                        # 경로 파일 제거함
                        changed_files_1.add(temp_str)

            changes_2 = p4.run("files", f"{folder_path_jp}@{start_datetime},{end_datetime}")
      

            changed_files_2 = set()
            diff_file_set_2 = set()
            desc_lists_2 = []

            for change in changes_2:
                _filename = change['depotFile']
                if (folder_path_2.replace("...", "")) in _filename:
                    temp_str = _filename
                    if "String" not in temp_str:
                        diff_file_set_2.add(temp_str)
                        # 경로 파일 제거함
                        changed_files_jp.add(temp_str)
  
            popup_file_list1 = []
            popup_file_list2 = []
            unexamed_file = []
            diff_file_list_1 = sorted(diff_file_set_1)
            diff_file_list_2 = sorted(diff_file_set_2)
            diff1 = [item for item in changed_files_1 if item not in changed_files_2]
            diff2 = []
            new_1_list = []
            new_2_list = []
            differences = set()
            for item in changed_files_2:
                if item not in changed_files_1:
                    diff2.append(item)
            if diff1:
                self.create_popup(f"-", f"{diff1}")
                new_2_list = sorted(diff_file_list_2 + diff1)
            else:
                new_2_list = diff_file_list_2
            if diff2:
                self.create_popup(f"-", f"{diff2}")
                new_1_list = sorted(diff_file_list_tw + diff2)
            else:
                new_1_list = diff_file_list_1
            today = datetime.datetime.now()
            one_year_ago = today - datetime.timedelta(days=365)
            one_year_ago_str = one_year_ago.strftime("%Y/%m/%d")
            for _1 in (new_1_list):
                if "xls" in _1 and "String" not in _1:
                    new_2 = _1.replace("_", "_").replace("", "")
                    try:
                        1_content = p4.run_print(f"-m1", f"{_1}@{one_year_ago_str},{end_datetime}")[1]
                        2_content = p4.run_print(f"-m1", f"{new_2}@{one_year_ago_str},{end_datetime}")[1]
                        if 1_content == 2_content:
                            pass
                        else:
                            # 로컬 PC에 저장해서 1000행씩만 읽어와서 비교하기
                            _local_file_path_1 = os.path.join(local_folder_path, f"{os.path.basename(_1)}_1")
                            with open(_local_file_path_1, "wb") as file:
                                file.write(1_content)
                            print(f"File saved to {_local_file_path_1}")
                            _local_file_path_2 = os.path.join(local_folder_path, f"{os.path.basename(new_2)}_2")
                            with open(_local_file_path_2, "wb") as file:
                                file.write(2_content)
                            print(f"File saved to {_local_file_path_2}")

                            _xls1 = pd.ExcelFile(_local_file_path_1)
                            _xls2 = pd.ExcelFile(_local_file_path_2)
                            sheets1 = _xls1.sheet_names
                            sheets2 = _xls2.sheet_names
                            common_sheets = set(sheets1) & set(sheets2)
                            for sheet in common_sheets:
                                if "#" in sheet:
                                    continue
                                print(f"시트: {sheet} 데이터 비교 시작")
                                csv_path_1 = os.path.join(local_folder_path, f"{os.path.basename()")
                                csv_path_2 = os.path.join(local_folder_path, f"{os.path.basename()")
                                df_1 = pd.read_excel(_local_file_path_1, sheet_name=sheet)
                                df_1.to_csv(csv_path_1, index=False)
                                del df_1
                                df_2 = pd.read_excel(_local_file_path_2, sheet_name=sheet)
                                df_2.to_csv(csv_path_2, index=False)
                                del df_2

                                chunk_size = 1000
                                chunk_iter_1 = pd.read_csv(csv_path_1, chunksize=chunk_size)
                                chunk_iter_2 = pd.read_csv(csv_path_2, chunksize=chunk_size)
                                # 청크 인덱스 초기화
                                chunk_index = 0
                                # 동시에 두 파일의 청크를 순회
                                for chunk_1, chunk_2 in zip(chunk_iter_1, chunk_iter_2):
                                    chunk_index += 1

                                    # 청크가 빈 경우에 대한 검사
                                    if chunk_1.empty and chunk_2.empty:
                                        break

                                    # 청크 비교
                                    if not chunk_1.equals(chunk_2):
                                        differences.add(f"{_1}_{sheet}")
                                        print(f"청크 {chunk_index} 차이 있음")
                                    else:
                                        print(f"청크 {chunk_index} 동일함")
                    except Exception as e:
                        unexamed_file.append(_1 + "(" + f"{e}" + ")")
            self.create_popup("다른 데이터:", f"{differences}")
            self.create_popup("확인 못 한 파일:", f"{unexamed_file}")

        except Exception as e:
            self.create_popup("P4 Error:", e)
            input("Press Enter to exit...")
        finally:
            p4.disconnect()

if __name__ == "__main__":
    root = tk.Tk()
    app = DateTimePickerApp(root)
    root.mainloop()
