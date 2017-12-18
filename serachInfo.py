import pytest


def save(data):
    pymysql = pytest.importorskip('pymysql')
    conn = pymysql.connect(host='*', port=3306, user='out', passwd='123456', db='jol', charset='utf8')
    cursor = conn.cursor()
    for di in data:
        for key,value in di.items():
            if(key == 'from_to_station_name'):
                value = ("-").join(value.split("\n"))
            print(key, value)
        # cursor.execute("select id from new_type where name='" + place.lower() + "'")
        # row_1 = cursor.fetchone()
        # cursor.execute("select nick from users where user_id=%s", ('20154206108',))
        # row_2 = cursor.fetchone()
        # if (len(row_1) and len(row_2)):
        #     flat = list(row_1)[0]
        #     name = list(row_2)[0]
        #     #             print(flat)
        #     print(name)
        #     cursor.execute("insert into new_title(flat,username,subject) values(%s,%s,%s);", (flat, name, subject))
    # conn.commit()
    cursor.close()
    conn.close()



# a = tickets.Cli('长沙','张家界','2017-11-26').run()
# a = [{'station_train_code': 'K9036', 'from_to_station_name': '长沙\n张家界', 'start_arrive_time': '04:26\n09:40', 'lishi': '05:14', 'first_class_seat': '--', 'second_class_seat': '--', 'soft_sleep': '--', 'hard_sleep': '无', 'soft_seat': '--', 'hard_seat': '有', 'no_seat': '--'}, {'station_train_code': 'K966', 'from_to_station_name': '长沙\n张家界', 'start_arrive_time': '06:04\n11:22', 'lishi': '05:18', 'first_class_seat': '--', 'second_class_seat': '--', 'soft_sleep': '13', 'hard_sleep': '有', 'soft_seat': '--', 'hard_seat': '有', 'no_seat': '--'}, {'station_train_code': 'K9026', 'from_to_station_name': '长沙\n张家界', 'start_arrive_time': '07:22\n12:06', 'lishi': '04:44', 'first_class_seat': '--', 'second_class_seat': '--', 'soft_sleep': '--', 'hard_sleep': '--', 'soft_seat': '--', 'hard_seat': '有', 'no_seat': '--'}, {'station_train_code': 'K1376', 'from_to_station_name': '长沙\n张家界', 'start_arrive_time': '07:28\n12:58', 'lishi': '05:30', 'first_class_seat': '--', 'second_class_seat': '--', 'soft_sleep': '4', 'hard_sleep': '有', 'soft_seat': '--', 'hard_seat': '有', 'no_seat': '--'}, {'station_train_code': 'K810', 'from_to_station_name': '长沙\n张家界', 'start_arrive_time': '11:29\n17:24', 'lishi': '05:55', 'first_class_seat': '--', 'second_class_seat': '--', 'soft_sleep': '7', 'hard_sleep': '有', 'soft_seat': '--', 'hard_seat': '有', 'no_seat': '--'}, {'station_train_code': 'T8322', 'from_to_station_name': '长沙\n张家界', 'start_arrive_time': '18:32\n22:58', 'lishi': '04:26', 'first_class_seat': '--', 'second_class_seat': '--', 'soft_sleep': '--', 'hard_sleep': '--', 'soft_seat': '有', 'hard_seat': '--', 'no_seat': '--'}, {'station_train_code': 'K9064', 'from_to_station_name': '长沙\n张家界', 'start_arrive_time': '22:16\n03:41', 'lishi': '05:25', 'first_class_seat': '--', 'second_class_seat': '--', 'soft_sleep': '11', 'hard_sleep': '有', 'soft_seat': '--', 'hard_seat': '有', 'no_seat': '--'}]
# save(a)