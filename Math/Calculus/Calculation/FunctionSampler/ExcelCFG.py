props13 = [
    '一阶或二阶可导（一元）：f(x)在区间区间(a,b)内具有k阶导数',
    '偏导数存在（多元）：f(x,y)在趋区域D内存在一阶偏导fx(x,y)和fy(x,y)，且D内处处可求偏导',
    '连续性（一元）：f(x)在开（闭）区间a到b上连续',
    '可微性（多元）：f(x,y)在点(x0,y0)处可微，满足可微的极限定义式等于0',
    '极限存在（一元）：f(x)在x趋于x0时极限存在，且极限等于A',
    '连续性（多元）：f(x,y)在区域D上连续，D内任意点处f(x,y)的极限等于f(x,y)在该点处的函数值',
    '周期性（一元）：f(x)是以T为周期的周期函数，满足f(x+T)=f(x)',
    '可定积分（一元）：f(x)在开（闭）区间a到b上可积，且定积分值等于常数k',
    '二阶偏导连续（多元）：f(x,y)在区域D内的二阶偏导数均连续，满足fxy(x,y)=fyx(x,y)（混合偏导相等）',
    '奇函数（一元）：f(x)在定义域内满足f(-x)=-f(x)',
    '偶函数（一元）：f(x)在定义域内满足f(-x)=f(x)',
    '相切（一元）：f(x)在点(x0,f(x0))处与直线y=kx+b相切',
    '反常积分收敛（一元）：被积函数为f(x)的无穷积分/瑕积分（若无瑕点，则在无穷限上积分）收敛到常数C'
]
op1 = [
    '相反数（-f(x)=g(x)或-f(x,y)=g(x,y)）',
    '绝对值（|f(x)|=g(x)或|f(x,y)|=g(x,y)）',
    '取倒数（1/f(x)=g(x)或1/f(x,y)=g(x,y)）',
    '平方（f(x)²=g(x)或f(x,y)²=g(x,y)）',
    '立方（f(x)³=g(x)或f(x,y)³=g(x,y)）',
    '平方根（sqrt(f(x))=g(x)或sqrt(f(x,y))=g(x,y)）',
    '立方根（curt(f(x))=g(x)或curt(f(x,y))=g(x,y)）',
    '向上取整（ceil(f(x))=g(x)或ceil(f(x,y))=g(x,y)）',
    '向下取整（floor(f(x))=g(x)或floor(f(x,y))=g(x,y)）'
]
op2 = [
    '加减（f(x)±g(x)=h(x)或f(x,y)±g(x,y)=h(x,y)）',
    '乘法（f(x)*g(x)=h(x)或f(x,y)*g(x,y)=h(x,y)）',
    '除法（f(x)/g(x)=h(x)或f(x,y)/g(x,y)=h(x,y)）',
    '取最大值（max(f(x),g(x))=h(x)或max(f(x,y),g(x,y))=h(x,y)）',
    '取最小值（min(f(x),g(x))=h(x)或min(f(x,y),g(x,y))=h(x,y)）',
    '复合函数（f(g(x))=h(x)或h(f(x,y),g(x,y))=h(x,y)）'
]
props13_short = [prop.split('：')[0] for prop in props13]
op1_short = [op.split('（')[0] for op in op1]
op2_short = [op.split('（')[0] for op in op2]
props13_desc = [prop.split('：')[1] for prop in props13]
op1_desc = [op.split('（')[1].strip('）') for op in op1]
op2_desc = [op.split('（')[1].strip('）') for op in op2]
combo2_sheet_name = '二元组合'
combo2_row_map = {'00': 2, '01': 3, '10': 4, '11': 5}
combo2_col_range = ['B', 'C', 'D', 'E']
combo3_sheet_name = '三元组合'
combo3_row_map = {'000': 2, '001': 3, '010': 4, '011': 5, '100': 6, '101': 7, '110': 8, '111': 9}
combo3_col_range = ['B', 'C', 'D', 'E', 'F']
op1_sheet_name = '一元运算'
op2_sheet_name = '二元运算'
op1_variation_code = ['00', '01', '10', '11']
op2_variation_code = ['000', '001', '010', '011', '100', '101', '110', '111']
op2_row_index = [2, 9, 16, 25, 32, 39]
file_path = 'resources/抽象函数.xlsx'
