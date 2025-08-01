<template>
  <div class="chart-cards">
    <!-- Statistics Cards Row -->
    <div class="row g-4 mb-4" v-if="statsCards.length > 0">
      <div 
        v-for="(card, index) in statsCards" 
        :key="index"
        :class="getCardColumnClass(statsCards.length)"
      >
        <div class="stat-card" :class="`stat-card-${card.type || 'primary'}`">
          <div class="stat-icon">
            <i :class="card.icon"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ formatStatValue(card.value) }}</div>
            <div class="stat-label">{{ card.label }}</div>
            <div class="stat-change" v-if="card.change" :class="getChangeClass(card.change)">
              <i :class="getChangeIcon(card.change)"></i>
              {{ Math.abs(card.change) }}%
            </div>
          </div>
          <div class="stat-trend" v-if="card.trend">
            <canvas :ref="el => trendChartRefs[index] = el" width="60" height="30"></canvas>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Charts Row -->
    <div class="row g-4" v-if="charts.length > 0">
      <div 
        v-for="(chart, index) in charts" 
        :key="index"
        :class="chart.colClass || 'col-md-6'"
      >
        <div class="chart-card" :class="chart.cardClass">
          <div class="chart-header">
            <div class="chart-title-section">
              <h5 class="chart-title">
                <i :class="chart.icon" v-if="chart.icon"></i>
                {{ chart.title }}
              </h5>
              <p class="chart-subtitle" v-if="chart.subtitle">
                {{ chart.subtitle }}
              </p>
            </div>
            <div class="chart-actions" v-if="chart.actions">
              <div class="dropdown" v-if="chart.timeRanges">
                <button 
                  class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                  type="button" 
                  :id="`timeRange${index}`"
                  data-bs-toggle="dropdown"
                >
                  {{ getSelectedTimeRange(chart.selectedTimeRange) }}
                </button>
                <ul class="dropdown-menu" :aria-labelledby="`timeRange${index}`">
                  <li v-for="range in chart.timeRanges" :key="range.value">
                    <a 
                      class="dropdown-item" 
                      href="#" 
                      @click.prevent="updateTimeRange(index, range.value)"
                      :class="{ active: chart.selectedTimeRange === range.value }"
                    >
                      {{ range.label }}
                    </a>
                  </li>
                </ul>
              </div>
              <button 
                v-if="chart.exportable" 
                class="btn btn-sm btn-outline-primary"
                @click="exportChart(index)"
                title="Export Chart"
              >
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
          
          <div class="chart-body">
            <!-- Loading State -->
            <div v-if="chart.loading" class="chart-loading">
              <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <p class="loading-text">{{ chart.loadingText || 'Loading chart data...' }}</p>
            </div>
            
            <!-- Error State -->
            <div v-else-if="chart.error" class="chart-error">
              <div class="error-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <p class="error-text">{{ chart.error }}</p>
              <button class="btn btn-sm btn-outline-primary" @click="retryChart(index)">
                <i class="fas fa-redo"></i> Retry
              </button>
            </div>
            
            <!-- Empty State -->
            <div v-else-if="chart.isEmpty" class="chart-empty">
              <div class="empty-icon">
                <i :class="chart.emptyIcon || 'fas fa-chart-bar'"></i>
              </div>
              <p class="empty-text">{{ chart.emptyText || 'No data available' }}</p>
            </div>
            
            <!-- Chart Canvas -->
            <div v-else class="chart-container" :class="chart.containerClass">
              <canvas 
                :ref="el => chartRefs[index] = el" 
                :style="{ height: chart.height || '300px' }"
              ></canvas>
            </div>
          </div>
          
          <!-- Chart Footer -->
          <div class="chart-footer" v-if="chart.footer">
            <div class="chart-legend" v-if="chart.legend">
              <div 
                v-for="(item, legendIndex) in chart.legend" 
                :key="legendIndex"
                class="legend-item"
              >
                <span 
                  class="legend-color" 
                  :style="{ backgroundColor: item.color }"
                ></span>
                <span class="legend-label">{{ item.label }}</span>
                <span class="legend-value" v-if="item.value">{{ item.value }}</span>
              </div>
            </div>
            <div class="chart-summary" v-if="chart.summary">
              <small class="text-muted">{{ chart.summary }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  LineController,
  BarController,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  LineController,
  BarController,
  Title,
  Tooltip,
  Legend,
  Filler
)

export default {
  name: 'ChartCards',
  props: {
    statsCards: {
      type: Array,
      default: () => []
    },
    charts: {
      type: Array,
      default: () => []
    },
    theme: {
      type: String,
      default: 'light',
      validator: (value) => ['light', 'dark'].includes(value)
    }
  },
  emits: ['chart-updated', 'time-range-changed', 'chart-export'],
  setup(props, { emit }) {
    const chartInstances = ref([])
    const trendChartInstances = ref([])
    const chartRefs = ref([])
    const trendChartRefs = ref([])
    
    // Chart color schemes
    const colorSchemes = {
      primary: ['#3B82F6', '#1E40AF', '#60A5FA', '#2563EB'],
      success: ['#22C55E', '#16A34A', '#4ADE80', '#15803D'],
      warning: ['#F59E0B', '#EAB308', '#FBBF24', '#D97706'],
      danger: ['#EF4444', '#DC2626', '#F87171', '#B91C1C'],
      info: ['#0EA5E9', '#0284C7', '#38BDF8', '#0369A1'],
      gradient: ['#3B82F6', '#0EA5E9', '#22C55E', '#F59E0B']
    }
    
    // Methods
    const getCardColumnClass = (count) => {
      if (count <= 2) return 'col-md-6'
      if (count <= 3) return 'col-md-4'
      if (count <= 4) return 'col-lg-3 col-md-6'
      return 'col-xl-2 col-lg-3 col-md-4 col-sm-6'
    }
    
    const formatStatValue = (value) => {
      if (typeof value === 'number') {
        if (value >= 1000000) {
          return (value / 1000000).toFixed(1) + 'M'
        }
        if (value >= 1000) {
          return (value / 1000).toFixed(1) + 'K'
        }
        return value.toLocaleString()
      }
      return value
    }
    
    const getChangeClass = (change) => {
      return change > 0 ? 'stat-change-positive' : 'stat-change-negative'
    }
    
    const getChangeIcon = (change) => {
      return change > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'
    }
    
    const getSelectedTimeRange = (value) => {
      const ranges = {
        '7d': 'Last 7 Days',
        '30d': 'Last 30 Days',
        '90d': 'Last 3 Months',
        '1y': 'Last Year',
        'all': 'All Time'
      }
      return ranges[value] || 'Select Range'
    }
    
    const updateTimeRange = (chartIndex, timeRange) => {
      emit('time-range-changed', { chartIndex, timeRange })
    }
    
    const exportChart = (chartIndex) => {
      const chartInstance = chartInstances.value[chartIndex]
      if (chartInstance) {
        const url = chartInstance.toBase64Image()
        emit('chart-export', { chartIndex, url, chart: props.charts[chartIndex] })
      }
    }
    
    const retryChart = (chartIndex) => {
      emit('chart-updated', { chartIndex, action: 'retry' })
    }
    
    const createChart = (canvasRef, chartConfig, index) => {
      if (!canvasRef) return null
      
      const ctx = canvasRef.getContext('2d')
      
      // Apply theme-based styling
      const themeConfig = getThemeConfig(chartConfig)
      
      const config = {
        ...chartConfig,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: chartConfig.showLegend !== false,
              position: 'bottom',
              labels: {
                usePointStyle: true,
                padding: 20,
                color: props.theme === 'dark' ? '#ffffff' : '#374151'
              }
            },
            tooltip: {
              backgroundColor: props.theme === 'dark' ? '#374151' : '#ffffff',
              titleColor: props.theme === 'dark' ? '#ffffff' : '#374151',
              bodyColor: props.theme === 'dark' ? '#ffffff' : '#374151',
              borderColor: props.theme === 'dark' ? '#4b5563' : '#e5e7eb',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: true
            },
            ...chartConfig.options?.plugins
          },
          scales: chartConfig.type !== 'doughnut' && chartConfig.type !== 'pie' ? {
            x: {
              grid: {
                color: props.theme === 'dark' ? '#374151' : '#f3f4f6'
              },
              ticks: {
                color: props.theme === 'dark' ? '#9ca3af' : '#6b7280'
              }
            },
            y: {
              grid: {
                color: props.theme === 'dark' ? '#374151' : '#f3f4f6'
              },
              ticks: {
                color: props.theme === 'dark' ? '#9ca3af' : '#6b7280'
              }
            },
            ...chartConfig.options?.scales
          } : undefined,
          ...chartConfig.options
        }
      }
      
      // Apply color scheme
      if (config.data?.datasets) {
        config.data.datasets = config.data.datasets.map((dataset, datasetIndex) => {
          const colors = colorSchemes[chartConfig.colorScheme || 'primary']
          return {
            ...dataset,
            backgroundColor: dataset.backgroundColor || colors[datasetIndex % colors.length] + '20',
            borderColor: dataset.borderColor || colors[datasetIndex % colors.length],
            borderWidth: dataset.borderWidth || 2
          }
        })
      }
      
      return new Chart(ctx, config)
    }
    
    const getThemeConfig = (chartConfig) => {
      // Return theme-specific configuration
      return {
        backgroundColor: props.theme === 'dark' ? '#1f2937' : '#ffffff',
        color: props.theme === 'dark' ? '#ffffff' : '#374151'
      }
    }
    
    const createTrendChart = (canvasRef, data) => {
      if (!canvasRef || !data) return null
      
      const ctx = canvasRef.getContext('2d')
      
      return new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels || [],
          datasets: [{
            data: data.values || [],
            borderColor: '#3498db',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { enabled: false }
          },
          scales: {
            x: { display: false },
            y: { display: false }
          },
          elements: {
            point: { radius: 0 }
          }
        }
      })
    }
    
    const initializeCharts = async () => {
      await nextTick()
      
      // Destroy existing chart instances
      chartInstances.value.forEach(chart => chart?.destroy())
      trendChartInstances.value.forEach(chart => chart?.destroy())
      chartInstances.value = []
      trendChartInstances.value = []
      
      // Create main charts
      props.charts.forEach((chart, index) => {
        const canvasRef = chartRefs.value[index]
        if (canvasRef && chart.config) {
          const chartInstance = createChart(canvasRef, chart.config, index)
          chartInstances.value[index] = chartInstance
        }
      })
      
      // Create trend charts for stat cards
      props.statsCards.forEach((card, index) => {
        if (card.trend) {
          const canvasRef = trendChartRefs.value[index]
          if (canvasRef) {
            const trendInstance = createTrendChart(canvasRef, card.trend)
            trendChartInstances.value[index] = trendInstance
          }
        }
      })
    }
    
    // Watchers
    watch(
      () => [props.charts, props.statsCards, props.theme],
      () => {
        initializeCharts()
      },
      { deep: true }
    )
    
    // Lifecycle hooks
    onMounted(() => {
      initializeCharts()
    })
    
    onUnmounted(() => {
      chartInstances.value.forEach(chart => chart?.destroy())
      trendChartInstances.value.forEach(chart => chart?.destroy())
    })
    
    return {
      chartInstances,
      trendChartInstances,
      chartRefs,
      trendChartRefs,
      getCardColumnClass,
      formatStatValue,
      getChangeClass,
      getChangeIcon,
      getSelectedTimeRange,
      updateTimeRange,
      exportChart,
      retryChart
    }
  }
}
</script>

<style scoped>
/* Stat Cards */
.stat-card {
  background: white;
  border-radius: var(--qm-border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--qm-shadow);
  transition: var(--qm-transition);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--qm-shadow-hover);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
}

.stat-card-success::before {
  background: var(--success);
}

.stat-card-warning::before {
  background: #F59E0B;
}

.stat-card-danger::before {
  background: var(--danger);
}

.stat-card-info::before {
  background: var(--secondary);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--qm-border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  flex-shrink: 0;
}

.stat-card-success .stat-icon {
  background: var(--success);
}

.stat-card-warning .stat-icon {
  background: #F59E0B;
}

.stat-card-danger .stat-icon {
  background: var(--danger);
}

.stat-card-info .stat-icon {
  background: var(--secondary);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-subtle);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-change {
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-change-positive {
  color: var(--success);
}

.stat-change-negative {
  color: var(--danger);
}

.stat-trend {
  width: 80px;
  height: 40px;
  flex-shrink: 0;
}

/* Chart Cards */
.chart-card {
  background: white;
  border-radius: var(--qm-border-radius-lg);
  box-shadow: var(--qm-shadow);
  transition: var(--qm-transition);
  overflow: hidden;
}

.chart-card:hover {
  box-shadow: var(--qm-shadow-hover);
}

.chart-header {
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.chart-title-section {
  flex: 1;
  min-width: 0;
}

.chart-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-title i {
  color: var(--qm-electric-blue);
}

.chart-subtitle {
  font-size: 0.875rem;
  color: var(--qm-medium-gray);
  margin: 0.25rem 0 0;
}

.chart-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-body {
  padding: 1rem 1.5rem;
  position: relative;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 300px;
}

/* Chart States */
.chart-loading,
.chart-error,
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  text-align: center;
}

.loading-spinner {
  margin-bottom: 1rem;
}

.loading-text,
.error-text,
.empty-text {
  color: var(--qm-medium-gray);
  font-size: 0.9rem;
  margin: 0;
}

.error-icon,
.empty-icon {
  font-size: 3rem;
  color: var(--qm-medium-gray);
  margin-bottom: 1rem;
  opacity: 0.5;
}

.error-icon {
  color: var(--qm-error-red);
}

/* Chart Footer */
.chart-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f5f9;
  background: #fafbfc;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-label {
  color: var(--qm-dark-gray);
  font-weight: 500;
}

.legend-value {
  color: var(--qm-medium-gray);
  font-weight: 600;
}

.chart-summary {
  margin-top: 0.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .stat-card {
    padding: 1rem;
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 1.25rem;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
  
  .chart-header {
    padding: 1rem;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-body {
    padding: 1rem;
  }
  
  .chart-container {
    height: 250px;
  }
  
  .chart-legend {
    justify-content: center;
  }
}

/* Dark Theme */
@media (prefers-color-scheme: dark) {
  .stat-card,
  .chart-card {
    background: #1f2937;
    color: white;
  }
  
  .stat-number {
    color: white;
  }
  
  .chart-title {
    color: white;
  }
  
  .chart-header {
    border-bottom-color: #374151;
  }
  
  .chart-footer {
    background: #111827;
    border-top-color: #374151;
  }
  
  .legend-label {
    color: white;
  }
}
</style>