# 定义 test_data 为全局变量，包含多组温度、测量值和目标值，若要修改测试数据，只需修改此处
test_data = [
    (-9, 430, 839),
    (9, 630, 839),
    (22, 720, 839),
    (28, 800, 839),
    (41, 900, 839),
    (53, 1000, 839)
]

# 定义 preset_points 为全局变量，包含预设的温度和初始补偿系数，方便修改预设数据
preset_points = [(-10, 0.700), (10, 0.900), (20, 0.980), (30, 1.000), (40, 1.015), (50, 1.025)]


# 定义智能温度补偿器类，用于管理温度补偿相关操作
class SmartTemperatureCompensator:
    def __init__(self, tolerance=2.0):
        # 补偿容忍度，用于判断是否需要调整补偿系数
        self.tolerance = tolerance
        # 存储预设的温度值
        self.temps = []
        # 存储预设的补偿系数
        self.factors = []

    def initialize(self, preset_points):
        # 解包预设点数据，分别得到温度和补偿系数
        self.temps, self.factors = zip(*preset_points)
        # 将温度转换为列表形式
        self.temps = list(self.temps)
        # 将补偿系数转换为列表形式
        self.factors = list(self.factors)

    def auto_adjust(self, temp, measured, target):
        try:
            # 计算目标补偿系数
            target_factor = target / measured
            index = 0
            # 查找温度所在的区间索引
            while index < len(self.temps) - 1 and temp > self.temps[index + 1]:
                index += 1

            # 判断目标补偿系数与当前补偿系数的差值是否在容忍度范围内
            if abs(target_factor - self.get_compensation(temp)) <= self.tolerance:
                # 更新当前区间的补偿系数
                self.factors[index] = target_factor
                # 更新后续区间的补偿系数
                self._update_subsequent_factors(index)
                # 更新前面区间的补偿系数
                self._update_previous_factors(index)

                # 打印更新后的温度补偿系数
                print(f"{temp}℃ 的温度补偿系数为: {target_factor:.4f}")
        except ZeroDivisionError:
            # 处理测量值为 0 的情况，打印错误信息
            print(f"错误：在调整 {temp}℃ 时，测量值为 0，无法计算补偿系数。")

    def get_compensation(self, temp):
        # 计算每个测试数据点的补偿系数
        compensated_data = [(t, target / measured) for t, measured, target in test_data]
        # 对补偿数据按温度进行排序
        compensated_data.sort()

        if temp < compensated_data[0][0]:
            return None
        if temp > compensated_data[-1][0]:
            return None

        for i in range(len(compensated_data) - 1):
            if compensated_data[i][0] <= temp < compensated_data[i + 1][0]:
                # 获取当前区间的左温度和左补偿系数
                left_temp, left_factor = compensated_data[i]
                # 获取当前区间的右温度和右补偿系数
                right_temp, right_factor = compensated_data[i + 1]
                # 计算斜率
                slope = (right_factor - left_factor) / (right_temp - left_temp)
                # 根据线性插值计算补偿系数
                return left_factor + slope * (temp - left_temp)
        return compensated_data[-1][1]

    def get_initial_compensation(self, temp):
        for i in range(len(self.temps) - 1):
            if self.temps[i] <= temp < self.temps[i + 1]:
                # 获取当前区间的左温度
                left_temp = self.temps[i]
                # 获取当前区间的右温度
                right_temp = self.temps[i + 1]
                # 获取当前区间的左补偿系数
                left_factor = self.factors[i]
                # 获取当前区间的右补偿系数
                right_factor = self.factors[i + 1]
                # 计算斜率
                slope = (right_factor - left_factor) / (right_temp - left_temp)
                # 根据线性插值计算补偿系数
                return left_factor + slope * (temp - left_temp)
        return self.factors[-1]

    def _update_subsequent_factors(self, index):
        if index < len(self.temps) - 1:
            # 获取当前区间的左温度
            left_temp = self.temps[index]
            # 获取当前区间的右温度
            right_temp = self.temps[index + 1]
            # 获取当前区间的左补偿系数
            left_factor = self.factors[index]
            # 获取当前区间的右补偿系数
            right_factor = self.factors[index + 1]
            # 计算斜率
            slope = (right_factor - left_factor) / (right_temp - left_temp)
            for i in range(index + 1, len(self.temps)):
                if self.temps[i] < right_temp:
                    self.factors[i] = left_factor + slope * (self.temps[i] - left_temp)

    def _update_previous_factors(self, index):
        if index > 0:
            # 获取前一个区间的左温度
            left_temp = self.temps[index - 1]
            # 获取当前区间的温度
            right_temp = self.temps[index]
            # 获取前一个区间的左补偿系数
            left_factor = self.factors[index - 1]
            # 获取当前区间的补偿系数
            right_factor = self.factors[index]
            # 计算斜率
            slope = (right_factor - left_factor) / (right_temp - left_temp)
            for i in range(index):
                if self.temps[i] > left_temp:
                    self.factors[i] = left_factor + slope * (self.temps[i] - left_temp)


if __name__ == "__main__":
    # 创建智能温度补偿器对象，设置容忍度为 2.0
    compensator = SmartTemperatureCompensator(tolerance=2.0)
    # 初始化补偿器的预设点
    compensator.initialize(preset_points)

    # 倒推实际测试数据
    new_test_data = []
    for temp, measured, target in test_data:
        # 获取初始补偿系数
        initial_compensation = compensator.get_initial_compensation(temp)
        # 倒推实际测量值
        actual_measured = measured / initial_compensation
        new_test_data.append((temp, actual_measured, target))

    # 更新 test_data
    test_data = new_test_data

    for temp, measured, target in test_data:
        print(f"\n=== 调整 {temp}℃ (测得={measured:.2f} → 目标={target}) ===")
        compensator.auto_adjust(temp, measured, target)

    # 定义计算补偿系数的函数，调用补偿器的 get_compensation 方法
    def calculate_compensation(temperature):
        return compensator.get_compensation(temperature)

    # 定义需要计算补偿系数的温度数组
    temperatures = [-10, 10, 20, 30, 40, 50]
    for temp in temperatures:
        compensation_value = calculate_compensation(temp)
        if compensation_value is not None:
            print(f"{temp}℃ 的温度补偿值为: {compensation_value:.4f}")
        else:
            print(f"无法计算 {temp}℃ 的温度补偿值。")
    