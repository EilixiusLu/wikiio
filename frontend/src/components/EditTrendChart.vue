<template>
  <div ref="chartRef" class="edit-trend-chart"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  chartData: {
    type: Array,
    default: () => [],
  },
})

const chartRef = ref(null)
let chartInstance = null
let resizeObserver = null

function resolveCSS(varName) {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
}

function buildOption() {
  const primary = resolveCSS('--color-primary')
  const hairline = resolveCSS('--color-hairline')
  const muted = resolveCSS('--color-muted')
  const canvas = resolveCSS('--color-canvas')
  const ink = resolveCSS('--color-ink')

  const dates = props.chartData.map(d => d.date)
  const counts = props.chartData.map(d => d.count)

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: canvas,
      borderColor: hairline,
      borderWidth: 1,
      textStyle: { color: ink, fontSize: 13 },
    },
    grid: {
      left: 40,
      right: 20,
      top: 20,
      bottom: 30,
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: hairline } },
      axisTick: { lineStyle: { color: hairline } },
      axisLabel: { color: muted, fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: hairline } },
      axisLabel: { color: muted, fontSize: 11 },
    },
    series: [
      {
        type: 'line',
        data: counts,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: primary, width: 2 },
        itemStyle: { color: primary },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: primary + '33' },
            { offset: 1, color: primary + '08' },
          ]),
        },
      },
    ],
  }
}

function renderChart() {
  if (!chartInstance) return
  chartInstance.setOption(buildOption(), true)
}

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  renderChart()

  resizeObserver = new ResizeObserver(() => {
    chartInstance?.resize()
  })
  resizeObserver.observe(chartRef.value)
})

watch(() => props.chartData, renderChart, { deep: true })

onUnmounted(() => {
  resizeObserver?.disconnect()
  chartInstance?.dispose()
})
</script>

<style scoped>
.edit-trend-chart {
  width: 100%;
  height: 100%;
}
</style>
