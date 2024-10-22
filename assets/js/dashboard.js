const chart1 = echarts.init(document.querySelector('#chart-1'));
const chart2 = echarts.init(document.querySelector('#chart-2'));
const chart3 = echarts.init(document.querySelector('#chart-3'));
let chart1_option = {
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow'
        },
        formatter: function (params) {
            let tar;
            if (params[1] && params[1].value !== '-') {
                tar = params[1];
            } else {
                tar = params[2];
            }
            return tar && tar.name + '<br/>' + tar.seriesName + ' : ' + tar.value;
        }
    },
    legend: {
        data: ['Expenses', 'Income']
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        data: (function () {
            let list = [];
            for (let i = 1; i <= 11; i++) {
                list.push('Nov ' + i);
            }
            return list;
        })()
    },
    yAxis: {
        type: 'value'
    },
    series: [
        {
            name: 'Placeholder',
            type: 'bar',
            stack: 'Total',
            silent: true,
            itemStyle: {
                borderColor: 'transparent',
                color: 'transparent'
            },
            emphasis: {
                itemStyle: {
                    borderColor: 'transparent',
                    color: 'transparent'
                }
            },
            data: [0, 900, 1245, 1530, 1376, 1376, 1511, 1689, 1856, 1495, 1292]
        },
        {
            name: 'Income',
            type: 'bar',
            stack: 'Total',
            label: {
                show: true,
                position: 'top'
            },
            data: [900, 345, 393, '-', '-', 135, 178, 286, '-', '-', '-']
        },
        {
            name: 'Expenses',
            type: 'bar',
            stack: 'Total',
            label: {
                show: true,
                position: 'bottom'
            },
            data: ['-', '-', '-', 108, 154, '-', '-', '-', 119, 361, 203]
        }
    ]
};
chart1.setOption(chart1_option)

function getVirtualData(year) {
    const date = +echarts.time.parse(year + '-01-01');
    const end = +echarts.time.parse(+year + 1 + '-01-01');
    const dayTime = 3600 * 24 * 1000;
    const data = [];
    for (let time = date; time < end; time += dayTime) {
        data.push([
            echarts.time.format(time, '{yyyy}-{MM}-{dd}', false),
            Math.floor(Math.random() * 10000)
        ]);
    }
    return data;
}
let chart2_option = {
    title: {
        top: 30,
        left: 'center',
        text: 'Daily Step Count'
    },
    tooltip: {},
    visualMap: {
        min: 0,
        max: 10000,
        type: 'piecewise',
        orient: 'horizontal',
        left: 'center',
        top: 65
    },
    calendar: {
        top: 120,
        left: 30,
        right: 30,
        cellSize: ['auto', 13],
        range: '1582',
        itemStyle: {
            borderWidth: 0.5
        },
        yearLabel: { show: false }
    },
    series: {
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data: getVirtualData('1582')
    }
};
chart2.setOption(chart2_option)

const labelRight = {
    position: 'right'
};
let chart3_option = {
    title: {
        text: 'Bar Chart with Negative Value'
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow'
        }
    },
    grid: {
        top: 80,
        bottom: 30
    },
    xAxis: {
        type: 'value',
        position: 'top',
        splitLine: {
            lineStyle: {
                type: 'dashed'
            }
        }
    },
    yAxis: {
        type: 'category',
        axisLine: { show: false },
        axisLabel: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        data: [
            'ten',
            'nine',
            'eight',
            'seven',
            'six',
            'five',
            'four',
            'three',
            'two',
            'one'
        ]
    },
    series: [
        {
            name: 'Cost',
            type: 'bar',
            stack: 'Total',
            label: {
                show: true,
                formatter: '{b}'
            },
            data: [
                { value: -0.07, label: labelRight },
                { value: -0.09, label: labelRight },
                0.2,
                0.44,
                { value: -0.23, label: labelRight },
                0.08,
                { value: -0.17, label: labelRight },
                0.47,
                { value: -0.36, label: labelRight },
                0.18
            ]
        }
    ]
};
chart3.setOption(chart3_option)

document.querySelector('#lblTopN').innerHTML = document.querySelector('#rngTopN').value
document.querySelector('#rngTopN').addEventListener('input', event => {
    document.querySelector('#lblTopN').innerHTML = event.target.value
})


document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(
    tabEl => tabEl.addEventListener('shown.bs.tab', event => {
        const text = event.target.textContent.trim().replaceAll(/\s+/g, ' ')
        if (text === 'Income vs Expenses') {
            chart1.resize()
        } else if (text === 'Transactions by Week') {
            chart2.resize()
        } else if (text === 'Top N Transactions') {
            chart3.resize()
        }
    })
)