<template>
  <div class="scpfd-page">
    <div class="scpfd-header">
      <span class="back-btn" @click="router.push('/tools')">
        <i class="fa fa-arrow-left"></i> 工具箱
      </span>
      <h1>SCP-FD 分类代码生成器</h1>
      <p class="subtitle">快速生成符合规范的页面分类 WikiText 代码，支持条件联动</p>
      <p class="subtitle">具体分类说明参考 <a href="https://scpfoundation.fandom.com/zh/index.php?curid=1822" target="_blank">SCP-FD标签指导</a></p>
    </div>

    <div class="scpfd-layout">
      <!-- ── 左侧：表单 ── -->
      <div class="form-panel">

        <!-- 1. 基础类型 -->
        <div class="form-section">
          <h3>基础类型</h3>
          <div class="tag-group">
            <span
              v-for="opt in baseTypeOptions" :key="opt"
              class="tag-option"
              :class="{ active: baseType === opt }"
              @click="baseType = opt; onBaseTypeChange()"
            >{{ opt }}</span>
          </div>
        </div>

        <!-- 2. 子类型 -->
        <div class="form-section" v-if="subTypeOptions.length">
          <h3>子类型</h3>
          <div class="tag-group">
            <span
              v-for="opt in subTypeOptions" :key="opt"
              class="tag-option"
              :class="{ active: subType === opt }"
              @click="subType = opt"
            >{{ opt }}</span>
          </div>
        </div>

        <!-- 2b. Crossover (仅原创) -->
        <div class="form-section" v-if="baseType === '原创'">
          <div class="checkbox-row">
            <span
              class="tag-option checkbox-tag"
              :class="{ active: isCrossover }"
              @click="isCrossover = !isCrossover"
            >Crossover</span>
            <span class="checkbox-hint">勾选此项将添加 [[Category: Crossover]]</span>
          </div>
        </div>

        <!-- 3. 项目等级（仅原创收容物 / 原创玩笑收容物） -->
        <div class="form-section" v-if="showItemClasses">
          <h3>项目等级</h3>
          <div class="tag-group">
            <span
              v-for="opt in itemClassOptions" :key="opt"
              class="tag-option"
              :class="{ active: itemClasses.includes(opt) }"
              @click="toggleItem(opt, itemClasses)"
            >{{ opt }}</span>
          </div>
        </div>

        <!-- 4. 站点与独立分部 -->
        <div class="form-section">
          <h3>站点与独立分部</h3>
          <div class="tag-group">
            <span
              v-for="opt in siteOptions" :key="opt"
              class="tag-option"
              :class="{ active: sites.includes(opt) }"
              @click="toggleItem(opt, sites)"
            >{{ opt }}</span>
          </div>
        </div>

        <!-- 5. GOI 标签 -->
        <div class="form-section">
          <h3>GOI 标签</h3>
          <div class="tag-group">
            <span
              v-for="opt in goiOptions" :key="opt"
              class="tag-option"
              :class="{ active: gois.includes(opt) }"
              @click="toggleItem(opt, gois)"
            >{{ opt }}</span>
          </div>
        </div>

        <!-- 6. 其他标签 -->
        <div class="form-section">
          <h3>其他标签</h3>
          <input
            v-model="extraTagsStr"
            class="text-input"
            placeholder="用逗号分隔标签，如：深冻行动"
          />
        </div>
      </div>

      <!-- ── 右侧：预览 ── -->
      <div class="preview-panel">
        <div class="preview-sticky">
          <div class="preview-header">
            <h3>生成的 WikiText</h3>
            <button class="copy-btn" @click="copyCode">{{ copied ? '已复制！' : '一键复制' }}</button>
          </div>
          <pre class="code-block"><code>{{ generatedCode || '请先在左侧选择分类选项' }}</code></pre>
          <p class="preview-hint">将以上代码粘贴到 Fandom 页面的源代码编辑器底部即可。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

/* ── 选项定义 ── */

const baseTypeOptions = ['归档', '原创', '中心页', '工具页', '管理']

const subTypeMap = {
  '归档': ['归档收容物', '归档故事'],
  '原创': [
    '原创收容物', '原创玩笑收容物', '原创GOI格式', '原创故事',
    '玩笑故事', '艺作', '指导', '建议', '原创GOI', '原创职员',
    '职员档案', '原创站点', '独立分部', '机动特遣队',
  ],
  '中心页': [],
  '工具页': [],
  '管理': [],
}

const itemClassOptions = [
  'Safe', 'Euclid', 'Keter', 'Thaumiel', 'Neutralized',
  'Decommissioned', 'Apollyon', 'Archon', 'Explained',
  '等待分级', '机密等级',
]

const siteOptions = [
  'Site-ZH-02', 'Site-ZH-11', 'Site-ZH-19', 'Site-ZH-77',
  'SCP-EQ', 'SCP-MC', 'SCP-LO',
]

const goiOptions = [
  'SCP基金会', 'GOC', '混沌分裂者', '伊姆', 'A.I.C.G',
  'TheCompany', '国安十九局', '南极异常管理局', '五目神教',
  '月下术士', '奇幻生物公司', 'Society', 'T&A', '魔法少年联盟',
]

/* ── 表单状态 ── */

const baseType = ref('')
const subType = ref('')
const isCrossover = ref(false)
const itemClasses = ref([])
const sites = ref([])
const gois = ref([])
const extraTagsStr = ref('')
const copied = ref(false)

/* ── 计算属性 ── */

const subTypeOptions = computed(() => subTypeMap[baseType.value] || [])

const showItemClasses = computed(() =>
  ['原创收容物', '原创玩笑收容物'].includes(subType.value)
)

const extraTags = computed(() =>
  extraTagsStr.value
    .split(/[,，]/)
    .map(t => t.trim())
    .filter(Boolean)
)

const generatedCode = computed(() => {
  const lines = []

  if (baseType.value) {
    lines.push(`[[Category: ${baseType.value} ]]`)
  }
  if (subType.value) {
    lines.push(`[[Category: ${subType.value} ]]`)
  }
  if (isCrossover.value) {
    lines.push('[[Category: Crossover]]')
  }
  for (const cls of itemClasses.value) {
    lines.push(`[[Category: ${cls} ]]`)
  }
  for (const site of sites.value) {
    lines.push(`[[Category: ${site} ]]`)
  }
  for (const goi of gois.value) {
    lines.push(`[[Category: ${goi} ]]`)
  }
  for (const tag of extraTags.value) {
    lines.push(`[[Category: ${tag} ]]`)
  }

  return lines.join('\n')
})

/* ── 方法 ── */

function toggleItem(opt, targetArr) {
  const idx = targetArr.indexOf(opt)
  if (idx === -1) targetArr.push(opt)
  else targetArr.splice(idx, 1)
}

function onBaseTypeChange() {
  subType.value = ''
  isCrossover.value = false
  itemClasses.value = []
}

async function copyCode() {
  if (!generatedCode.value) return
  await navigator.clipboard.writeText(generatedCode.value)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}
</script>

<style scoped>
.scpfd-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-16) var(--space-6);
}

/* ── Header ── */

.scpfd-header {
  margin-bottom: var(--space-10);
}

.back-btn {
  display: inline-block;
  color: var(--color-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  margin-bottom: var(--space-4);
  transition: opacity var(--duration-fast) var(--ease-smooth);
}
.back-btn:hover { opacity: 0.7; }

.scpfd-header h1 {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-ink);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-2);
}

.subtitle {
  font-size: var(--text-base);
  color: var(--color-muted);
}

/* ── Layout ── */

.scpfd-layout {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: var(--space-8);
  align-items: start;
}

/* ── Form Panel ── */

.form-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.form-section h3 {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-3);
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tag-option {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill);
  font-size: var(--text-sm);
  background: var(--color-parchment);
  color: var(--color-muted);
  border: 1.5px solid transparent;
  cursor: pointer;
  user-select: none;
  transition: background-color var(--duration-fast) var(--ease-smooth),
              color var(--duration-fast) var(--ease-smooth),
              border-color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}

.tag-option:hover {
  background: var(--color-highlight);
  color: var(--color-primary);
}

.tag-option:active {
  transform: scale(0.96);
}

.tag-option.active {
  background: var(--color-highlight);
  color: var(--color-primary);
  border-color: var(--color-primary);
  font-weight: 500;
}

.checkbox-tag {
  margin-right: var(--space-2);
}

.checkbox-row {
  display: flex;
  align-items: center;
}

.checkbox-hint {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

/* ── Text Input ── */

.text-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-family: inherit;
  color: var(--color-ink);
  background: var(--color-canvas);
  outline: none;
  transition: border-color var(--duration-fast) var(--ease-smooth),
              box-shadow var(--duration-fast) var(--ease-smooth);
  box-sizing: border-box;
}

.text-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-highlight);
}

.text-input::placeholder {
  color: var(--color-muted);
}

/* ── Preview Panel ── */

.preview-panel {
  position: relative;
}

.preview-sticky {
  position: sticky;
  top: var(--space-6);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.preview-header h3 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-ink);
}

.copy-btn {
  padding: var(--space-2) var(--space-5);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-pill);
  font-size: var(--text-sm);
  font-family: inherit;
  cursor: pointer;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}

.copy-btn:hover { opacity: 0.9; }
.copy-btn:active { transform: scale(0.96); }

.code-block {
  background: var(--color-parchment);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6);
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
  font-size: var(--text-sm);
  line-height: 1.8;
  color: var(--color-ink);
  white-space: pre-wrap;
  word-break: break-all;
  min-height: 200px;
  max-height: 500px;
  overflow-y: auto;
}

.preview-hint {
  font-size: var(--text-xs);
  color: var(--color-muted);
  margin-top: var(--space-3);
}

/* ── Mobile ── */

@media (max-width: 768px) {
  .scpfd-layout {
    grid-template-columns: 1fr;
  }

  .preview-sticky {
    position: static;
  }

  .scpfd-header h1 {
    font-size: var(--text-xl);
  }
}
</style>
