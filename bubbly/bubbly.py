#!/usr/bin/env python
# coding=utf-8
"""
@Description   绘制气泡图
@Author        Alex_McAvoy
@Date          2025-07-10 15:54:36
"""
import numpy as np 
import pandas as pd

def bubbleplot(dataset: pd.DataFrame, x_column: str, y_column: str, 
               bubble_column: str, z_column: str = None,
               time_column: str = None, size_column: str = None, color_column: str = None,   
               x_logscale: bool = False, y_logscale: bool = False, z_logscale: bool = False, 
               x_range: list = None, y_range: list = None, z_range: list = None, 
               x_title: str = None, y_title: str = None, z_title: str = None, 
               title: str = None, colorbar_title: str = None,
               scale_bubble: float = 1, colorscale: str = None, 
               marker_opacity: float = None, marker_border_width: float = None, 
               show_slider: bool = True, show_button: bool = True, 
               show_colorbar: bool = True, show_legend: bool = None,
               width: int = None, height: int = None) -> dict:
    """
    @description 生成交互式且带动画效果的气泡图，支持二维或三维，并带时间滑块和分类图例
    @param {pd.DataFrame} dataset 数据集，包含所有绘图所需列
    @param {str} x_column x轴对应的列名
    @param {str} y_column y轴对应的列名
    @param {str} bubble_column 气泡文字内容对应的列名
    @param {str} z_column z轴对应的列名，若为空则绘制二维图
    @param {str} time_column 时间列名，生成动画帧
    @param {str} size_column 气泡大小对应的列名
    @param {str} color_column 气泡颜色对应的列名，支持数值和分类
    @param {bool} x_logscale x轴是否使用对数刻度
    @param {bool} y_logscale y轴是否使用对数刻度
    @param {bool} z_logscale z轴是否使用对数刻度
    @param {list} x_range x轴范围
    @param {list} y_range y轴范围
    @param {list} z_range z轴范围
    @param {str} x_title x轴标题
    @param {str} y_title y轴标题
    @param {str} z_title z轴标题
    @param {str} title 图表标题
    @param {str} colorbar_title 颜色条标题
    @param {float} scale_bubble 气泡大小缩放因子
    @param {str} colorscale plotly颜色映射表
    @param {float} marker_opacity 气泡透明度
    @param {float} marker_border_width 气泡边框宽度
    @param {bool} show_slider 是否显示时间滑块
    @param {bool} show_button 是否显示播放暂停按钮
    @param {bool} show_colorbar 是否显示颜色条
    @param {bool} show_legend 是否显示图例
    @param {int} width 图宽
    @param {int} height 图高
    @return {dict} 返回绘图的figure字典，包含数据和布局
    """
    
    # 初始化分类列变量，以区分分类颜色与数值颜色
    category_column = None
    # 判断是否指定颜色列
    if color_column: 
        # 判断颜色列是否为category、object、bool类型
        if dataset[color_column].dtype.name in ['category', 'object', 'bool']:
            # 作为分类列使用
            category_column = color_column
            # 取消数字颜色列
            color_column = None
    

    # 判断是否存在时间列
    if time_column:
        # 获取所有时间点
        years = dataset[time_column].unique()
    else:
        # 无时间轴数据
        years = None
        # 不显示时间滑块
        show_slider = False
        # 不显示按钮
        show_button = False
    

    # 需要处理的列名列表
    column_names = [x_column, y_column]
    # 判断是否有z轴
    if z_column:
        # 添加z轴列
        column_names.append(z_column)
        # 设为3D图
        axes3D = True
    else:
        # 设为2D图
        axes3D = False
    # 添加气泡文字列
    column_names.append(bubble_column)
    # 判断是否存在气泡大小列
    if size_column:
        # 添加气泡大小列
        column_names.append(size_column)
    # 判断是否存在气泡颜色列
    if color_column:
        # 添加气泡有颜色列
        column_names.append(color_column)
        

    # 判断是否存在分类列，以确定参数模板和用于绘图的数据网格DataFrame
    if category_column:
        # 获取分类类别
        categories = dataset[category_column].unique()
        # 三参数模板
        col_name_template = '{}+{}+{}_grid'
        # 使用带分类的数据网格DataFrame生成函数
        grid = makeGridWithCategories(dataset, column_names, time_column, category_column, years, categories)
        # 默认显示图例
        if show_legend is None:
            showlegend = True
        else: 
            showlegend = show_legend
    else:
        # 二参数模板
        col_name_template = '{}+{}_grid'
        # 普通的数据网格DataFrame
        grid = makeGrid(dataset, column_names, time_column, years)
        # 默认不显示图例
        if show_legend is None:
            showlegend = False
        else: 
            showlegend = show_legend
        
    # 判断是否显示时间滑块
    if show_slider:
        slider_scale = years
    else:
        slider_scale = None
    

    # 设置Figure字典、滑块配置字典
    figure, sliders_dict = setLayout(x_title, y_title, z_title, title, 
                                x_logscale, y_logscale, z_logscale, axes3D,
                                show_slider, slider_scale, show_button, showlegend, width, height)
    
    # 判断是否存在气泡大小列
    if size_column:
        # 计算气泡大小的参考值
        sizeref = 2.*max(dataset[size_column])/(scale_bubble*80**2)
    else:
        sizeref = None
        
    # 判断是否存在分类列
    if category_column:
        # 遍历分类列，以添加基础帧
        for category in categories:
            # 判断是否存在时间列
            if time_column:
                # 取最早的时间点
                year = min(years)
                # 格式化列名模板（唯一列标识）
                col_name_template_year = col_name_template.format(year, {}, {})
            else:
                # 无时间模板（唯一列标识）
                col_name_template_year = '{}+{}_grid'
            
            # 生成绘图的Trace数据
            trace = getTrace(grid, col_name_template_year, x_column, y_column, 
                              bubble_column, z_column, size_column, 
                              sizeref, scale_bubble, marker_opacity, marker_border_width,
                              category=category)
            # 判断是否有z轴
            if z_column:
                # 设为3D图
                trace['type'] = 'scatter3d'

            # 存入Trance数据
            figure['data'].append(trace)
           
        # 判断时间列是否存在，以添加时间帧
        if time_column:
            # 遍历年份
            for year in years:
                # 设置帧格式
                frame = {'data': [], 'name': str(year)}
                # 遍历每个类型
                for category in categories:
                    # 格式化列名模板（唯一列标识）
                    col_name_template_year = col_name_template.format(year, {}, {})
                    # 生成绘图的Trace数据
                    trace = getTrace(grid, col_name_template_year, x_column, y_column, 
                                      bubble_column, z_column, size_column, 
                                      sizeref, scale_bubble, marker_opacity, marker_border_width,
                                      category=category)
                    # 判断是否存在z轴
                    if z_column:
                        # 设为3D图
                        trace['type'] = 'scatter3d'
                    # 存入Trace数据
                    frame['data'].append(trace)
                # 存入帧数据
                figure['frames'].append(frame) 

                # 判断是否展示时间滑块
                if show_slider:
                    addSliderSteps(sliders_dict, year)           
    else:
        # 判断时间列是否存在，以确定列名模板
        if time_column:
            # 寻找时间最小的年份
            year = min(years)
            # 格式化列名模板（唯一列标识）
            col_name_template_year = col_name_template.format(year, {})
        else:
            # 无列名模板（唯一列标识）
            col_name_template_year = '{}_grid'

        # 获取绘图用Trace数据
        trace = getTrace(grid, col_name_template_year, x_column, y_column, 
                          bubble_column, z_column, size_column, 
                          sizeref, scale_bubble, marker_opacity, marker_border_width,
                          color_column, colorscale, show_colorbar, colorbar_title)
        # 判断是否存在z轴
        if z_column:
            trace['type'] = 'scatter3d'

        # 存在Trace数据
        figure['data'].append(trace)
        
        # 判断时间列是否存在，以添加时间帧
        if time_column:
            # 遍历所有年份
            for year in years:
                # 格式化列名模板（唯一列标识）
                col_name_template_year = col_name_template.format(year, {})
                # 设置时间帧数据格式
                frame = {'data': [], 'name': str(year)}
                # 获取绘图用的Trace数据
                trace = getTrace(grid, col_name_template_year, x_column, y_column, 
                                  bubble_column, z_column, size_column, 
                                  sizeref, scale_bubble, marker_opacity, marker_border_width,
                                  color_column, colorscale, show_colorbar, colorbar_title)
                # 判断z轴是否存在
                if z_column:
                    # 设为3D图
                    trace['type'] = 'scatter3d'
                # 存储帧
                frame['data'].append(trace)
                figure['frames'].append(frame) 
                # 判断是否显示时间滑块
                if show_slider:
                    addSliderSteps(sliders_dict, year) 
    
    # 若未显式指定x轴范围，根据x轴数据设置
    if x_range is None:
        x_range = setRange(dataset[x_column], x_logscale) 
    
    # 若未显式指定y轴范围，根据y轴数据设置
    if y_range is None:
        y_range = setRange(dataset[y_column], y_logscale)

    # 判断是否为3D图
    if axes3D:
        # 若未显式指定z轴范围，根据z轴数据设置
        if z_range is None:
            z_range = setRange(dataset[z_column], z_logscale)
        # 设置Figure中的x、y、z轴显示范围
        figure['layout']['scene']['xaxis']['range'] = x_range
        figure['layout']['scene']['yaxis']['range'] = y_range
        figure['layout']['scene']['zaxis']['range'] = z_range
    else:
        # 设置Figure中的x、y轴显示范围
        figure['layout']['xaxis']['range'] = x_range
        figure['layout']['yaxis']['range'] = y_range
    
    # 判断是否显示时间滑块，以在Figure中设置时间滑块
    if show_slider:
        figure['layout']['sliders'] = [sliders_dict]
     
    return figure

def makeGrid(dataset: pd.DataFrame, column_names: list, time_column: str = None, years: np.ndarray = None) -> pd.DataFrame:
    """
    @description 为绘图生成数据网格DataFrame，用于存储每个时间点或全局的列数据
    @param {pd.DataFrame} dataset 输入数据集
    @param {list} column_names 需要处理的列名列表
    @param {str} time_column 时间列名
    @param {np.ndarray} years 时间列唯一值数组
    @return {pd.DataFrame} 返回网格DataFrame，每行包含一个键名和对应列数据列表
    """
    # 数据网格
    grid = pd.DataFrame()
    # 判断是否存在时间列
    if time_column:
        # 定义列名模板
        col_name_template = '{}+{}_grid'
        # 若未指定年份数组，自动提取所有年份
        if years is None:
            years = dataset[time_column].unique()

        # 遍历所有年份
        for year in years:
            # 过滤数据集中当前年份数据
            dataset_by_year = dataset[(dataset[time_column] == int(year))]
            # 遍历所需列
            for col_name in column_names:
                # 根据模板拼接唯一列标识
                temp = col_name_template.format(year, col_name)
                # 若该列有数据
                if dataset_by_year[col_name].size != 0:
                    # 将该列数据封装为一行DataFrame后，再拼接到数据网格grid中
                    grid = pd.concat([grid, pd.DataFrame([{'value': list(dataset_by_year[col_name]), 'key': temp}])], ignore_index=True)
    else:
        # 遍历所需列
        for col_name in column_names:
            # 将该列数据封装为一行DataFrame后，再拼接到数据网格grid中
            grid = pd.concat([grid, pd.DataFrame([{'value': list(dataset[col_name]), 'key': col_name + '_grid'}])], ignore_index=True)
        
    return grid

def makeGridWithCategories(dataset: pd.DataFrame, column_names: list, time_column: str, category_column: str,
                           years: np.ndarray = None, categories: np.ndarray = None) -> pd.DataFrame:
    """
    @description 为绘图生成包含分类的数据网格DataFrame，用于在不同时间和类别下分别存储各列数据
    @param {pd.DataFrame} dataset 输入数据集
    @param {list} column_names 需要处理的列名列表
    @param {str} time_column 时间列名
    @param {str} category_column 分类列名
    @param {np.ndarray} years 时间列唯一值数组
    @param {np.ndarray} categories 分类列唯一值数组
    @return {pd.DataFrame} 返回网格DataFrame，每行包含一个键名和对应列数据列表
    """
    # 数据网格
    grid = pd.DataFrame()

    # 若未指定分类列数组，提取所有分类
    if categories is None:
        categories = dataset[category_column].unique()
    
    # 判断时间列是否存在
    if time_column:
        # 定义列名模板
        col_name_template = '{}+{}+{}_grid'
        # 若未指定年份数组，自动提取所有年份
        if years is None:
            years = dataset[time_column].unique()
        
        # 遍历所有年份
        for year in years:
            # 遍历所有类别
            for category in categories:
                # 根据年份与类别筛选
                dataset_by_year_and_cat = dataset[(dataset[time_column] == int(year)) & (dataset[category_column] == category)]
                # 遍历所需列
                for col_name in column_names:
                    # 根据模板拼接唯一列标识
                    temp = col_name_template.format(year, col_name, category)
                    # 若该列有数据
                    if dataset_by_year_and_cat[col_name].size != 0:
                        # 将该列数据封装为一行DataFrame后，再拼接到数据网格grid中
                        grid = pd.concat([grid, pd.DataFrame([{'value': list(dataset_by_year_and_cat[col_name]), 'key': temp}])], ignore_index=True)
    else:
        # 定义列名模板
        col_name_template = '{}+{}_grid'
        # 遍历所有类别
        for category in categories:
            # 根据类别筛选
            dataset_by_cat = dataset[(dataset[category_column] == category)]
            # 遍历所需列
            for col_name in column_names:
                # 根据模板拼接唯一列标识
                temp = col_name_template.format(col_name, category)
                # 若该列有数据
                if dataset_by_cat[col_name].size != 0:
                        # 将该列数据封装为一行DataFrame后，再拼接到数据网格grid中
                        grid = pd.concat([grid, pd.DataFrame([{'value': list(dataset_by_cat[col_name]), 'key': temp}])], ignore_index=True)
        
    return grid

def setLayout(x_title: str = None, y_title: str = None, z_title: str = None, title: str = None, x_logscale: bool = False,
               y_logscale: bool = False, z_logscale: bool = False, axes3D: bool = False, show_slider: bool = True, 
               slider_scale: np.ndarray = None, show_button: bool = True, show_legend: bool = False, width: int = None,
               height: int = None) -> tuple:
    """
    @description 创建绘图的布局字典，设置坐标轴、标题、滑块、按钮等，返回figure和滑块对象
    @param {str} x_title x轴标题
    @param {str} y_title y轴标题
    @param {str} z_title z轴标题
    @param {str} title 图表标题
    @param {bool} x_logscale x轴是否使用对数刻度
    @param {bool} y_logscale y轴是否使用对数刻度
    @param {bool} z_logscale z轴是否使用对数刻度
    @param {bool} axes3D 是否绘制三维图
    @param {bool} show_slider 是否显示时间滑块
    @param {np.ndarray} slider_scale 滑块范围
    @param {bool} show_button 是否显示播放按钮
    @param {bool} show_legend 是否显示图例
    @param {int} width 图宽
    @param {int} height 图高
    @return {tuple} 返回 (figure字典, 滑块配置字典)
    """
    
    # 定义Figure布局字典
    figure = {
        'data': [],
        'layout': {},
        'frames': []
    }
    
    # 判断是否为3D图
    if axes3D:
        # 获取3D图的Figure布局
        figure = set3Daxes(figure, x_title, y_title, z_title, x_logscale, y_logscale, z_logscale)
    else:
        # 获取2D图的Figure布局
        figure = set2Daxes(figure, x_title, y_title, x_logscale, y_logscale)
    
    # 设置标题、悬停交互、图例、外边距
    figure['layout']['title'] = title    
    figure['layout']['hovermode'] = 'closest'
    figure['layout']['showlegend'] = show_legend
    figure['layout']['margin'] = dict(b=50, t=50, pad=5)
    
    # 设置宽度
    if width:
        figure['layout']['width'] = width

    # 设置高度
    if height:
        figure['layout']['height'] = height
    
    # 设置时间滑块
    if show_slider: 
        sliders_dict = addSlider(figure, slider_scale)
    else:
        sliders_dict = {}
    
    # 设置按钮
    if show_button:
        addButton(figure)
        
    return figure, sliders_dict

def set2Daxes(figure: dict, x_title: str = None, y_title: str = None, x_logscale: bool = False, y_logscale: bool = False) -> dict:
    """
    @description 设置二维坐标轴配置（x、y）
    @param {dict} figure 当前figure字典
    @param {str} x_title x轴标题
    @param {str} y_title y轴标题
    @param {bool} x_logscale x轴是否使用对数刻度
    @param {bool} y_logscale y轴是否使用对数刻度
    @return {dict} 返回更新后的figure字典
    """
    
    # x轴、y轴配置
    figure['layout']['xaxis'] = {'title': x_title, 'autorange': False}
    figure['layout']['yaxis'] = {'title': y_title, 'autorange': False} 

    # x轴启用对数刻度
    if x_logscale:
        figure['layout']['xaxis']['type'] = 'log'
    # y轴启用对数刻度
    if y_logscale:
        figure['layout']['yaxis']['type'] = 'log'
        
    return figure
        
def set3Daxes(figure: dict, x_title: str = None, y_title: str = None, z_title: str = None, 
              x_logscale: bool = False, y_logscale: bool = False, z_logscale: bool = False) -> dict:
    """
    @description 设置三维坐标轴配置（x、y、z）
    @param {dict} figure 当前figure字典
    @param {str|None} x_title x轴标题
    @param {str|None} y_title y轴标题
    @param {str|None} z_title z轴标题
    @param {bool} x_logscale x轴是否使用对数刻度
    @param {bool} y_logscale y轴是否使用对数刻度
    @param {bool} z_logscale z轴是否使用对数刻度
    @return {dict} 返回更新后的figure字典
    """
    
    # 三维scene配置
    figure['layout']['scene'] = {}
    # x轴配置
    figure['layout']['scene']['xaxis'] = {'title': x_title, 'autorange': False}
    # y轴配置
    figure['layout']['scene']['yaxis'] = {'title': y_title, 'autorange': False} 
    # z轴配置
    figure['layout']['scene']['zaxis'] = {'title': z_title, 'autorange': False} 

    # x轴开启对数刻度
    if x_logscale:
        figure['layout']['scene']['xaxis']['type'] = 'log'
    # y轴开启对数刻度
    if y_logscale:
        figure['layout']['scene']['yaxis']['type'] = 'log'
    # z轴开启对数刻度
    if z_logscale:
        figure['layout']['scene']['zaxis']['type'] = 'log'
        
    return figure
        
def addSlider(figure: dict, slider_scale: np.ndarray) -> dict:
    """
    @description 创建并添加时间滑块到figure布局
    @param {dict} figure 当前figure字典
    @param {np.ndarray} slider_scale 时间滑块对应的时间刻度列表
    @return {dict} 返回滑块配置字典
    """
    
    # 设置初始滑块
    figure['layout']['sliders'] = {
        'args': [
            # 滑块触发参数
            'slider.value', {
                # 动画时长
                'duration': 400,
                # 动画插值
                'ease': 'cubic-in-out'
            }
        ],
        # 初始值
        'initialValue': min(slider_scale),
        # 触发动画
        'plotlycommand': 'animate',
        # 所有可选值
        'values': slider_scale,
        # 是否显示
        'visible': True
    }
    
    # 初始化时间滑块设置
    sliders_dict = {
        # 当前活动位置
        'active': 0,
        # y轴锚点
        'yanchor': 'top',
        # x轴锚点
        'xanchor': 'left',
        # 当前值显示设置
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Year:',
            'visible': True,
            'xanchor': 'right'
        },
        # 过渡动画
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        # 内边距
        'pad': {'b': 10, 't': 50},
        # 滑块长度
        'len': 0.9,
        # 滑块x轴位置
        'x': 0.1,
        # 滑块y轴位置
        'y': 0,
        # 滑块各步配置
        'steps': []
    }
    
    return sliders_dict

def addSliderSteps(sliders_dict: dict, year: int) -> None:
    """
    @description 向时间滑块中添加一个时间步
    @param {dict} sliders_dict 时间滑块配置字典
    @param {int} year 时间步对应的年份
    @return {None}
    """
    
    slider_step = {
        'args': [
            # 动画终止年份
            [year],
            {
                # 帧设置
                'frame': {'duration': 300, 'redraw': False},
                # 立即切换
                'mode': 'immediate',
                # 过渡设置
                'transition': {'duration': 300}
            }
        ],
        # 时间滑块标签
        'label': str(year),
        # 调用动画
        'method': 'animate'
    }
    # 添加到steps列表
    sliders_dict['steps'].append(slider_step)
    
def addButton(figure: dict) -> None:
    """
    @description 为figure添加播放/暂停按钮
    @param {dict} figure 当前figure字典
    @return {None}
    """
    
    figure['layout']['updatemenus'] = [
        {
            # 按钮配置
            'buttons': [
                # 播放按钮
                {
                    'args': [
                        None, 
                        {
                            # 帧设置
                            'frame': {'duration': 500, 'redraw': False},
                            # 是否从当前位置继续播放
                            'fromcurrent': True, 
                            # 过渡设置
                            'transition': {'duration': 300, 'easing': 'quadratic-in-out'}
                        }
                    ],
                    # 按钮标签
                    'label': 'Play',
                    # 调用动画
                    'method': 'animate'
                },
                # 暂停按钮
                {
                    'args': [
                        [None], 
                        {
                            # 帧设置
                            'frame': {'duration': 0, 'redraw': False},
                            # 立即切换
                            'mode': 'immediate', 
                            # 过渡设置
                            'transition': {'duration': 0}
                        }
                    ],
                    # 按钮标签
                    'label': 'Pause',
                    # 调用动画
                    'method': 'animate'
                }
            ],
            # 按钮排列方向
            'direction': 'left',
            # 内边距
            'pad': {'r': 10, 't': 87},
            # 按钮是否高亮
            'showactive': False,
            # 类型
            'type': 'buttons',
            # x轴锚点
            'xanchor': 'right',
            # y轴锚点
            'yanchor': 'top',
            # x轴位置
            'x': 0.1,
            # y轴位置
            'y': 0
        }
    ]
    
def setRange(values: np.ndarray, logscale: bool = False ) -> list:
    """
    @description 根据数值和是否对数刻度，自动计算坐标轴范围
    @param {np.ndarray} values 输入数值数组
    @param {bool} logscale 是否使用对数刻度
    @return {list} [最小值, 最大值]
    """
    
    # 是否使用对数刻度
    if logscale:
        # 对数刻度最小值
        rmin = min(np.log10(values))*0.97
        # 对数刻度最大值
        rmax = max(np.log10(values))*1.04
    else:
        # 普通刻度最小值
        rmin = min(values)*0.7
        # 普通刻度最大值
        rmax = max(values)*1.4
        
    return [rmin, rmax] 

def getTrace(grid: pd.DataFrame, col_name_template: str, x_column: str, y_column: str, bubble_column: str, z_column: str = None,
             size_column: str = None, sizeref: float = 200000, scale_bubble: float = 1, marker_opacity: float = None,
             marker_border_width: float = None, color_column: str = None, colorscale: str = None, show_colorbar: bool = True,
             colorbar_title: str = None, category: str = None ) -> dict:
    """
    @description 从grid中提取数据，生成一个trace字典
    @param {pd.DataFrame} grid 输入数据网格
    @param {str} col_name_template 列名模板
    @param {str} x_column x轴列名
    @param {str} y_column y轴列名
    @param {str} bubble_column 气泡标签列
    @param {str} z_column z轴列名
    @param {str} size_column 气泡大小列名
    @param {float} sizeref 气泡大小参考值
    @param {float} scale_bubble 气泡缩放倍数
    @param {float} marker_opacity 透明度
    @param {float} marker_border_width 边框宽度
    @param {str} color_column 颜色列名
    @param {str} colorscale 颜色映射
    @param {bool} show_colorbar 是否显示色条
    @param {str} colorbar_title 色条标题
    @param {str} category 分类
    @return {dict} 返回trace字典
    """
    
    # 初始配置
    trace = {
        # x轴
        'x': grid.loc[grid['key']==col_name_template.format(x_column, category), 'value'].values[0],
        # y轴
        'y': grid.loc[grid['key']==col_name_template.format(y_column, category), 'value'].values[0],
        # 气泡文字标签
        'text': grid.loc[grid['key']==col_name_template.format(bubble_column, category), 'value'].values[0],
        # 显示为散点
        'mode': 'markers'
    }
    
    # z轴
    if z_column:
        trace['z'] = grid.loc[grid['key']==col_name_template.format(z_column, category), 'value'].values[0]

    # 判断是否指定气泡尺寸
    if size_column:
        # 设置气泡尺寸
        trace['marker'] = {
            'sizemode': 'area',
            'sizeref': sizeref,
            'size': grid.loc[grid['key']==col_name_template.format(size_column, category), 'value'].values[0],
        }
    else:
        # 默认尺寸
        trace['marker'] = {
            'size': 10*scale_bubble,
        }
    
    # 透明度
    if marker_opacity:
        trace['marker']['opacity'] = marker_opacity

    # 边框宽度  
    if marker_border_width:
        trace['marker']['line'] = {'width': marker_border_width}
    
    # 颜色列
    if color_column:
        trace['marker']['color'] = grid.loc[grid['key']==col_name_template.format(color_column), 'value'].values[0]
        trace['marker']['colorbar'] = {'title': colorbar_title}
        trace['marker']['colorscale'] = colorscale
    
    # 分类名
    if category:
        trace['name'] = category
        
    return trace


