const chart1 = echarts.init(document.querySelector('#chart-1'));
const chart2 = echarts.init(document.querySelector('#chart-2'));
const chart3 = echarts.init(document.querySelector('#chart-3'));
let chart1_option = {
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow'
        },
        formatter: params => {
            const marker = params[0]['marker']
            const value = params[0]['value'][2] - params[0]['value'][1]
            const type = value >= 0 ? 'Income' : 'Expenses'
            function setValue(value) {
                return `<span class="tooltip-value">${value}</span>`
            }
            let details = ''
            const green = `<span class="marker marker-green"></span>`
            const red = `<span class="marker marker-red"></span>`
            params[0]['data']['details'].forEach(detail => {
                details += detail[1] >= 0 ? green : red
                details += " "
                details += detail[0]
                details += setValue(detail[1].toFixed(2))
                details += `<br>`
            })
            return `${marker} ${type} ${setValue(value.toFixed(2))}<hr>${details}`
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
        data: [],
        axisLine: {
            onZero: false
        },
        splitLine: {
            show: false
        }
    },
    yAxis: {
        type: 'value',
        // show: false
    },
    series: [
        {
            name: 'Income',
            type: 'candlestick',
            data: [],
            itemStyle: {
                color: '#47b262',
                borderColor: '#47b262'
            }
        },
        {
            name: 'Expenses',
            type: 'candlestick',
            data: [],
            itemStyle: {
                color: '#eb5454',
                borderColor: '#eb5454',
                color0: '#eb5454',
                borderColor0: '#eb5454'
            }
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

// Temporary using fetch api for Development, to be commented after online
// TODO: Use selenium inject CSV data into JS: driver.execute_script('func(arguments[0])', array)
let cache;
let fetch_promise;
function load_data() {
    if (cache) {
        // console.log('cache')
        return Promise.resolve(cache);
    } else if (fetch_promise) {
        // console.log('waiting')
        return fetch_promise
    } else {
        // console.log('not cache')
        fetch_promise = fetch('../../csv')
            .then(res => res.text())
            .then(text => {
                const el = document.createElement('html')
                el.innerHTML = text
                const a = el.querySelectorAll('#files a[href$=".csv"]')
                const datesEl = el.querySelectorAll('#files a[href$=".csv"] .date')
                const dates = (
                    [...datesEl]
                        .map((date, index) => ({ date: new Date(date.innerHTML), anchor: a[index] }))
                        .sort((a, b) => b.date.getTime() - a.date.getTime())
                )
                return fetch(dates[0].anchor.href)
            })
            .then(res => res.text())
            .then(data => {
                cache = Papa.parse(data, { skipEmptyLines: true, header: true }).data
                return cache;
            })
            .catch(error => console.error(error))
            .finally(() => fetch_promise = null)
        return fetch_promise
    }
}

// Populate Table
function populateTable(data) {
    data.forEach((d, index) => {
        const tr = document.querySelector('#temp-row').cloneNode(true).content.firstElementChild
        tr.querySelector('#tr-date-').textContent = d['Date']
        tr.querySelector('#tr-type-').textContent = d['Transaction Type']
        tr.querySelector('#tr-desc-').textContent = d['Description']
        tr.querySelector('#tr-amnt-').textContent = Math.abs(Number(d['Amount (RM)'])).toFixed(2)

        if (d['Amount (RM)'] < 0) {
            tr.classList.add('table-danger')
            tr.querySelector('.float-start').textContent = '-'
        } else {
            tr.classList.add('table-success')
        }
        tr.id += index
        tr.querySelector('#tr-date-').id += index
        tr.querySelector('#tr-type-').id += index
        tr.querySelector('#tr-desc-').id += index
        tr.querySelector('#tr-amnt-').id += index
        document.querySelector('tbody').appendChild(tr)
    })
    return data
}

function plotChart1(data) {
    const positive = []
    const negative = []
    const cumsum = [0]
    const dates = []
    const group = Object.groupBy(data, d => d['Date'])
    Object.entries(group).forEach((v, index) => {
        let current = 0
        const details = []
        v[1].forEach(d => {
            const amount = Number(d['Amount (RM)'])
            current += amount
            details.push([d['Description'], amount])
        })
        const previous = cumsum[index]
        const sum = current + previous
        cumsum.push(sum)
        const arr = [previous, sum, previous, sum]
        const d = {
            value: arr,
            details: details
        }
        if (current >= 0) {
            positive.push(d)
            negative.push('-')
        } else {
            positive.push('-')
            negative.push(d)
        }
        dates.push(new Date(v[0]).toISOString().split('T')[0])
    })
    chart1_option['xAxis']['data'] = dates
    chart1_option['series'][0]['data'] = positive
    chart1_option['series'][1]['data'] = negative
    chart1.setOption(chart1_option)
    return data
}

load_data()
    .then(populateTable)
    .then(plotChart1)

