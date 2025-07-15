# bubbly

******************************

基于 Plotly 绘制交互式动画与气泡图，可容纳 x 轴、y 轴、z 轴、时间、气泡、气泡大小、气泡颜色

该仓库基于原作者的代码进行了改进，修复了原作者所使用老版本 Pandas 没有 `append()` 而无法运行的错误

目前依赖包：

1. numpy == 1.25.0
2. pandas == 2.0.3
3. plotly == 5.18.0

原作者仓库地址详见：[AashitaK/bubbly](https://github.com/AashitaK/bubbly)

在 Jupyter Notebook 中的使用示例：

```python
from __future__ import division
from plotly.offline import init_notebook_mode, iplot
init_notebook_mode()

figure = bubbleplot(dataset=gapminder_indicators, x_column='gdpPercap', y_column='lifeExp', 
bubble_column='country', time_column='year',  size_column='pop', color_column='continent', 
x_title="GDP per Capita", y_title="Life Expectancy", title='Gapminder Global Indicators',
x_logscale=True, scale_bubble=3, height=650)
plot(figure, config={'scrollzoom': True})
```

效果图：

![效果图](https://github.com/Alex-McAvoy/bubbly/blob/master/images/bubble.gif)

关于该绘图函数，更多示例与说明请查阅原作者 Kaggle 项目页：[点击这里](https://www.kaggle.com/code/aashita/guide-to-animated-bubble-charts-using-plotly)

