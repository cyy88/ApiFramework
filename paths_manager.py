import os

# 获取当前文件所在目录，其实就是项目根目录
# 获取当前文件所在路径作为项目路径
project_path = os.path.dirname(__file__)

# 构造学校数据Excel文件的路径
add_school_data_xlsx = f'{project_path}/data/add_school_data.xlsx'

# 构造学校数据YAML文件的路径
data_yaml = f'{project_path}/data/data.yml'

# 构造数据库yaml文件路径
db_yaml = f'{project_path}/config/db.yml'

# 构造redis yaml文件路径
redis_yaml = f'{project_path}/config/redis.yml'

# 构造http域名yaml文件路径
http_yaml = f'{project_path}/config/http.yml'

# 构造基本数据yaml文件路径
common_yaml = f'{project_path}/config/common.yml'


