from data import KeyWord, all_job_analyst
from config import handle_config
import time


# 下载分析
# for item in handle_config.moniter:
#     instance = KeyWord(item)
#     if instance.last_update_more_than(days=14):
#         instance.update_all_data()
#         instance.del_redundancy()
#         instance.analyst_all()
#         print(item, '0k')
#         time.sleep(handle_config.item_download_interval)
#     else:
#         print(item, 'pass')


# 统计所有数据
# all_job_analyst()


# 分析所有
# for item in handle_config.moniter:
#     instance = KeyWord(item)
#     instance.analyst_all()
#     print(item, '0k')



