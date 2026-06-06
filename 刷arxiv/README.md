---
layout: page
title: 刷arxiv
description: 像短视频一样刷 arXiv 论文
---

<script setup>
import { computed, ref } from 'vue'

const categories = ['全部', 'cs.LG', 'cs.AI', 'cs.CV', 'cs.CL', 'robotics']

const papers = [
  {
    id: '2506.01001',
    accent: '#ff3b5c',
    initial: 'S',
    title: '智能体强化学习中的协作意图建模',
    originalTitle: 'Collaborative Intention Modeling for Agentic Reinforcement Learning',
    authors: 'Santiago Amaya-Corredor, Miguel Calvo-Fullana, Priya S. Nair',
    tags: ['cs.LG', 'cs.AI'],
    date: '6月1日',
    score: 902,
    summary:
      '针对智能体具有可分离动力学但需协调满足全局资源约束的系统，本文提出一种分布式约束多智能体强化学习方法。该方法将状态增强为局部意图和全局预算信号，在不共享隐私轨迹的情况下提升协作效率。',
    highlights: ['分布式约束优化', '可解释协作意图', '多智能体资源调度'],
    reason: '适合关注强化学习、分布式控制和具身智能协作的读者。',
    pdf: 'https://arxiv.org/pdf/2506.01001',
    abs: 'https://arxiv.org/abs/2506.01001',
  },
  {
    id: '2506.01002',
    accent: '#635bff',
    initial: 'M',
    title: '多智能体强化学习中的泛化意图建模',
    originalTitle: 'Generalizable Intent Models in Multi-Agent Reinforcement Learning',
    authors: 'Mateusz Odrowaz-Sypniewski, Jasmine Bayrooti, Akari Tan',
    tags: ['cs.LG', 'cs.MA'],
    date: '6月1日',
    score: 840,
    summary:
      '现有对手建模方法使用基于先验选择的片段信息来对手的下一步动作作假设，但缺少跨任务泛化能力。本文主张意图通常受任务和环境依赖约束，提出可迁移的意图表示。',
    highlights: ['跨任务泛化', '对手建模', '任务条件表示'],
    reason: '如果你在做 MARL 或策略泛化，这篇可以快速加入待读列表。',
    pdf: 'https://arxiv.org/pdf/2506.01002',
    abs: 'https://arxiv.org/abs/2506.01002',
  },
  {
    id: '2506.01003',
    accent: '#19c7c7',
    initial: 'H',
    title: 'Crafter：一个用于从多种输入生成可编辑科学图形的多智能体框架',
    originalTitle: 'Crafter: Multi-Agent Editable Scientific Figure Generation',
    authors: 'Haozhe Zhao, Shuzheng Si, Lina Park, +7 more',
    tags: ['cs.CV', 'cs.AI'],
    date: '6月1日',
    score: 781,
    summary:
      '科学图形制作是论文准备中最劳动密集的环节之一。本文提出多智能体框架 Crafter，可从文本、表格、草图和已有图像生成可编辑矢量图，并通过审稿式反馈循环改善布局。',
    highlights: ['可编辑矢量图', '多模态输入', '自动版式审稿'],
    reason: '非常适合科研写作工具、图表生成和多模态代理方向。',
    pdf: 'https://arxiv.org/pdf/2506.01003',
    abs: 'https://arxiv.org/abs/2506.01003',
  },
  {
    id: '2506.01004',
    accent: '#34c759',
    initial: 'Z',
    title: '智能体强化学习中的技能复用即时压缩',
    originalTitle: 'Prompt-Time Compression for Skill Reuse in Agentic RL',
    authors: 'Zhikun Xu, Yu Feng, Meiling Wu, +4 more',
    tags: ['cs.LG'],
    date: '6月1日',
    score: 736,
    summary:
      '基于强化学习的大语言模型智能体常学习脆弱任务特定捷径。本文提出 ReuseRL，在推理前从成功轨迹中抽取可复用技能，并压缩为可检索的短提示片段。',
    highlights: ['技能复用', '轨迹压缩', '长程任务泛化'],
    reason: '对 agent 训练、prompt memory 和工具使用有直接启发。',
    pdf: 'https://arxiv.org/pdf/2506.01004',
    abs: 'https://arxiv.org/abs/2506.01004',
  },
  {
    id: '2506.01005',
    accent: '#2bb8ff',
    initial: 'A',
    title: '强化学习中的终结表征',
    originalTitle: 'Terminal Representations for Robust Reinforcement Learning',
    authors: 'Amir Esterhuysen, Anders Jonsson',
    tags: ['cs.LG'],
    date: '6月1日',
    score: 694,
    summary:
      '针对现有后继表征与默认表征在稀疏奖励问题中收敛慢、泛化弱的问题，本文提出终结表征 TR。TR 类似于对 DR 编码奖励加权后的状态分布，可更稳定地传播目标信息。',
    highlights: ['稀疏奖励', '表征学习', '更稳定的值传播'],
    reason: '适合强化学习理论和表征学习读者。',
    pdf: 'https://arxiv.org/pdf/2506.01005',
    abs: 'https://arxiv.org/abs/2506.01005',
  },
  {
    id: '2506.01006',
    accent: '#ff9f0a',
    initial: 'L',
    title: '长上下文语言模型的检索边界诊断',
    originalTitle: 'Diagnosing Retrieval Boundaries in Long-Context Language Models',
    authors: 'Lena Hoffmann, Rui Zhang, Mateo Silva',
    tags: ['cs.CL', 'cs.AI'],
    date: '6月1日',
    score: 671,
    summary:
      '论文构造多粒度干扰集，分析长上下文模型在远距离证据、冲突证据和隐式引用场景中的检索边界。作者发现注意力峰值并不总能解释答案来源。',
    highlights: ['长上下文评测', '检索鲁棒性', '可解释诊断'],
    reason: '如果你关心 RAG、长文档问答或模型评测，这篇值得收藏。',
    pdf: 'https://arxiv.org/pdf/2506.01006',
    abs: 'https://arxiv.org/abs/2506.01006',
  },
  {
    id: '2506.01007',
    accent: '#af52de',
    initial: 'R',
    title: '视觉语言动作模型的安全回放评测',
    originalTitle: 'Safety Replay Evaluation for Vision-Language-Action Models',
    authors: 'Rina Okabe, Tom Walsh, Chenxi Li, +5 more',
    tags: ['robotics', 'cs.CV'],
    date: '6月1日',
    score: 628,
    summary:
      '作者提出一套机器人离线安全回放协议，在不真实执行危险动作的情况下评估 VLA 模型。系统会把历史视觉轨迹、自然语言指令和动作约束组合成可复现实验。',
    highlights: ['机器人安全', 'VLA 评测', '离线回放协议'],
    reason: '适合机器人、具身智能和安全评测方向快速扫读。',
    pdf: 'https://arxiv.org/pdf/2506.01007',
    abs: 'https://arxiv.org/abs/2506.01007',
  },
]

const activeCategory = ref('全部')
const activeTab = ref('discover')
const query = ref('')
const selectedPaper = ref(papers[0])
const likedIds = ref(['2506.01003'])
const savedIds = ref(['2506.01006'])
const readIds = ref([])
const feedPulse = ref(0)

const filteredPapers = computed(() => {
  const keyword = query.value.trim().toLowerCase()
  return papers.filter((paper) => {
    const categoryMatched =
      activeCategory.value === '全部' || paper.tags.includes(activeCategory.value)
    const keywordMatched =
      !keyword ||
      [paper.title, paper.originalTitle, paper.authors, paper.summary, paper.tags.join(' ')]
        .join(' ')
        .toLowerCase()
        .includes(keyword)

    if (activeTab.value === 'saved') {
      return savedIds.value.includes(paper.id) && categoryMatched && keywordMatched
    }

    return categoryMatched && keywordMatched
  })
})

const todayScore = computed(() => papers.reduce((sum, paper) => sum + paper.score, 0))
const savedCount = computed(() => savedIds.value.length)
const readCount = computed(() => readIds.value.length)
const likedCount = computed(() => likedIds.value.length)

function toggleInList(listRef, id) {
  if (listRef.value.includes(id)) {
    listRef.value = listRef.value.filter((item) => item !== id)
  } else {
    listRef.value = [...listRef.value, id]
  }
}

function openPaper(paper) {
  selectedPaper.value = paper
  if (!readIds.value.includes(paper.id)) {
    readIds.value = [...readIds.value, paper.id]
  }
}

function refreshFeed() {
  const index = categories.indexOf(activeCategory.value)
  activeCategory.value = categories[(index + 1) % categories.length]
  feedPulse.value += 1
}

function clearSearch() {
  query.value = ''
  activeTab.value = 'discover'
}
</script>

<div class="arxiv-page">
  <section class="hero-card">
    <p class="eyebrow">Swipe arXiv</p>
    <h1>像刷短视频一样刷论文</h1>
    <p>
      点击论文卡片进入摘要详情，底部可以切换发现、收藏、设置和搜索；分类、搜索、喜欢与收藏状态会即时更新。
    </p>
  </section>

  <section class="phone-stage" aria-label="刷 arXiv 应用预览">
    <div class="ambient ambient-one"></div>
    <div class="ambient ambient-two"></div>

    <div class="phone-frame">
      <div class="phone-glass">
        <div class="status-bar">
          <span>09:41</span>
          <span class="dynamic-island"></span>
          <span>5G 85%</span>
        </div>

        <header class="app-header">
          <button class="icon-button" type="button" aria-label="返回">‹</button>
          <div>
            <strong>6月1日</strong>
            <span>({{ todayScore }})</span>
          </div>
          <button class="icon-button" type="button" aria-label="菜单">☰</button>
        </header>

        <div class="quick-stats">
          <button
            v-for="category in categories"
            :key="category"
            class="chip"
            :class="{ active: activeCategory === category }"
            type="button"
            @click="activeCategory = category"
          >
            {{ category }}
          </button>
        </div>

        <label class="search-box" :class="{ searching: query }">
          <span>⌕</span>
          <input v-model="query" type="search" placeholder="搜标题、作者或方向" />
          <button v-if="query" type="button" @click="clearSearch">清除</button>
        </label>

        <main class="paper-feed" :class="{ pulse: feedPulse % 2 === 1 }" aria-live="polite">
          <article
            v-for="(paper, index) in filteredPapers"
            :key="paper.id"
            class="paper-item"
            :class="{ read: readIds.includes(paper.id) }"
            @click="openPaper(paper)"
          >
            <div class="rank">#{{ index + 1 }}</div>
            <div class="avatar" :style="{ background: paper.accent }">{{ paper.initial }}</div>
            <div class="paper-copy">
              <div class="paper-meta">
                <span v-for="tag in paper.tags" :key="tag">{{ tag }}</span>
              </div>
              <h2>{{ paper.title }}</h2>
              <p class="authors">{{ paper.authors }}</p>
              <p class="summary">{{ paper.summary }}</p>
              <div class="item-actions">
                <button
                  type="button"
                  :class="{ active: likedIds.includes(paper.id) }"
                  @click.stop="toggleInList(likedIds, paper.id)"
                >
                  ♥
                </button>
                <button
                  type="button"
                  :class="{ active: savedIds.includes(paper.id) }"
                  @click.stop="toggleInList(savedIds, paper.id)"
                >
                  ☆
                </button>
                <a :href="paper.abs" target="_blank" rel="noreferrer" @click.stop>arXiv</a>
              </div>
            </div>
          </article>

          <div v-if="filteredPapers.length === 0" class="empty-state">
            <strong>没有找到匹配论文</strong>
            <p>换个关键词，或回到“全部”继续刷。</p>
            <button type="button" @click="clearSearch">重置</button>
          </div>
        </main>

        <footer class="bottom-nav">
          <button
            type="button"
            :class="{ active: activeTab === 'discover' }"
            @click="activeTab = 'discover'"
          >
            <span>▣</span>
            发现
          </button>
          <button
            type="button"
            :class="{ active: activeTab === 'saved' }"
            @click="activeTab = 'saved'"
          >
            <span>♥</span>
            收藏 {{ savedCount }}
          </button>
          <button type="button" @click="refreshFeed">
            <span>↻</span>
            换一批
          </button>
          <button
            type="button"
            :class="{ active: activeTab === 'search' }"
            @click="activeTab = 'search'"
          >
            <span>⌕</span>
            搜索
          </button>
        </footer>

        <aside v-if="selectedPaper" class="detail-sheet">
          <button class="close-detail" type="button" aria-label="关闭详情" @click="selectedPaper = null">
            ×
          </button>
          <div class="detail-tags">
            <span v-for="tag in selectedPaper.tags" :key="tag">{{ tag }}</span>
          </div>
          <h2>{{ selectedPaper.title }}</h2>
          <p class="original-title">{{ selectedPaper.originalTitle }}</p>
          <p class="authors">{{ selectedPaper.authors }}</p>
          <p>{{ selectedPaper.summary }}</p>
          <div class="highlight-grid">
            <span v-for="point in selectedPaper.highlights" :key="point">{{ point }}</span>
          </div>
          <p class="reason">{{ selectedPaper.reason }}</p>
          <div class="detail-actions">
            <a :href="selectedPaper.pdf" target="_blank" rel="noreferrer">打开 PDF</a>
            <button
              type="button"
              :class="{ active: savedIds.includes(selectedPaper.id) }"
              @click="toggleInList(savedIds, selectedPaper.id)"
            >
              {{ savedIds.includes(selectedPaper.id) ? '已收藏' : '收藏' }}
            </button>
          </div>
        </aside>
      </div>
    </div>
  </section>

  <section class="feature-strip">
    <div>
      <strong>{{ papers.length }}</strong>
      <span>今日论文</span>
    </div>
    <div>
      <strong>{{ likedCount }}</strong>
      <span>已喜欢</span>
    </div>
    <div>
      <strong>{{ savedCount }}</strong>
      <span>已收藏</span>
    </div>
    <div>
      <strong>{{ readCount }}</strong>
      <span>已点开</span>
    </div>
  </section>
</div>

<style scoped>
.arxiv-page {
  min-height: 100vh;
  margin: -32px auto 0;
  padding: 40px 18px 72px;
  color: #101114;
  background:
    radial-gradient(circle at top left, rgba(255, 59, 92, 0.2), transparent 34%),
    radial-gradient(circle at 90% 10%, rgba(99, 91, 255, 0.16), transparent 32%),
    linear-gradient(180deg, #f7f3ef 0%, #f5f7fb 54%, #eff3f8 100%);
}

.hero-card {
  max-width: 820px;
  margin: 0 auto 28px;
  padding: 28px;
  border: 1px solid rgba(18, 18, 20, 0.08);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 24px 70px rgba(21, 29, 48, 0.08);
  backdrop-filter: blur(18px);
}

.eyebrow {
  margin: 0 0 8px;
  color: #ff2d55;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.hero-card h1 {
  margin: 0;
  font-size: clamp(34px, 7vw, 72px);
  line-height: 1.02;
  letter-spacing: -0.06em;
}

.hero-card p:last-child {
  max-width: 660px;
  margin: 16px 0 0;
  color: #646b76;
  font-size: 16px;
}

.phone-stage {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 760px;
  overflow: hidden;
  border-radius: 40px;
  background:
    radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.28), transparent 28%),
    linear-gradient(135deg, #0a0a0c, #232328 42%, #0b0b0e);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.ambient {
  position: absolute;
  width: 340px;
  height: 340px;
  border-radius: 999px;
  filter: blur(16px);
  opacity: 0.46;
}

.ambient-one {
  top: 46px;
  left: 12%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.24), transparent 68%);
}

.ambient-two {
  right: 12%;
  bottom: 40px;
  background: radial-gradient(circle, rgba(255, 45, 85, 0.18), transparent 66%);
}

.phone-frame {
  position: relative;
  z-index: 1;
  width: min(390px, calc(100vw - 44px));
  height: 720px;
  padding: 12px;
  border: 2px solid rgba(255, 255, 255, 0.76);
  border-radius: 48px;
  background: linear-gradient(140deg, #24242a, #050506);
  box-shadow:
    0 42px 90px rgba(0, 0, 0, 0.48),
    inset 0 0 0 2px rgba(255, 255, 255, 0.16);
}

.phone-glass {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  border-radius: 36px;
  background: rgba(255, 255, 255, 0.97);
}

.status-bar {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 12px 20px 8px;
  color: #0c0d10;
  font-size: 13px;
  font-weight: 800;
}

.status-bar span:last-child {
  text-align: right;
}

.dynamic-island {
  width: 96px;
  height: 28px;
  border-radius: 999px;
  background: #050506;
}

.app-header {
  display: grid;
  grid-template-columns: 42px 1fr 42px;
  align-items: center;
  padding: 2px 16px 10px;
  text-align: center;
}

.app-header strong {
  font-size: 20px;
}

.app-header span {
  margin-left: 4px;
  color: #5d6470;
  font-size: 13px;
}

.icon-button,
.chip,
.item-actions button,
.bottom-nav button,
.close-detail,
.detail-actions button,
.empty-state button,
.search-box button {
  border: 0;
  cursor: pointer;
  font: inherit;
}

.icon-button {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  color: #1a1c20;
  background: #f2f3f5;
  font-size: 22px;
}

.quick-stats {
  display: flex;
  gap: 7px;
  overflow-x: auto;
  padding: 0 16px 10px;
  scrollbar-width: none;
}

.quick-stats::-webkit-scrollbar {
  display: none;
}

.chip {
  flex: 0 0 auto;
  padding: 7px 12px;
  border-radius: 999px;
  color: #666d79;
  background: #f0f2f5;
  font-size: 12px;
  font-weight: 700;
}

.chip.active {
  color: #fff;
  background: #111318;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px 10px;
  padding: 9px 12px;
  border-radius: 18px;
  background: #f3f5f8;
  color: #8a9099;
}

.search-box.searching {
  box-shadow: inset 0 0 0 1px rgba(255, 45, 85, 0.28);
}

.search-box input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  background: transparent;
  color: #15171c;
  font: inherit;
  font-size: 13px;
}

.search-box button {
  padding: 3px 8px;
  border-radius: 999px;
  color: #ff2d55;
  background: rgba(255, 45, 85, 0.1);
  font-size: 12px;
}

.paper-feed {
  flex: 1;
  overflow-y: auto;
  padding: 0 14px 100px;
  scroll-snap-type: y proximity;
  scrollbar-width: thin;
}

.paper-feed.pulse .paper-item:first-child {
  animation: card-pop 0.35s ease both;
}

.paper-item {
  position: relative;
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 10px;
  padding: 14px 4px 14px 0;
  border-bottom: 1px solid #eceef2;
  scroll-snap-align: start;
}

.paper-item.read {
  opacity: 0.72;
}

.rank {
  position: absolute;
  left: 46px;
  top: 3px;
  color: #9aa1ac;
  font-size: 11px;
  font-weight: 800;
}

.avatar {
  display: grid;
  place-items: center;
  width: 31px;
  height: 31px;
  margin-top: 18px;
  border-radius: 999px;
  color: #fff;
  font-size: 14px;
  font-weight: 800;
}

.paper-copy {
  min-width: 0;
}

.paper-meta {
  display: flex;
  gap: 7px;
  margin-left: 34px;
  color: #9aa1ac;
  font-size: 11px;
  font-weight: 700;
}

.paper-item h2 {
  display: -webkit-box;
  overflow: hidden;
  margin: 2px 0 2px;
  color: #16181d;
  font-size: 14px;
  line-height: 1.28;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.authors,
.summary {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: #6b7280;
  line-height: 1.45;
  -webkit-box-orient: vertical;
}

.authors {
  font-size: 12px;
  -webkit-line-clamp: 1;
}

.summary {
  margin-top: 3px;
  font-size: 12px;
  -webkit-line-clamp: 3;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.item-actions button,
.item-actions a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 26px;
  padding: 0 8px;
  border-radius: 999px;
  color: #9ba2ad;
  background: #f4f5f7;
  font-size: 12px;
  font-weight: 800;
  text-decoration: none;
}

.item-actions button.active {
  color: #ff2d55;
  background: rgba(255, 45, 85, 0.1);
}

.empty-state {
  margin: 36px 10px;
  padding: 28px 18px;
  border-radius: 24px;
  text-align: center;
  background: #f6f7f9;
}

.empty-state p {
  margin: 8px 0 16px;
  color: #7a818c;
  font-size: 13px;
}

.empty-state button {
  padding: 9px 16px;
  border-radius: 999px;
  color: #fff;
  background: #111318;
}

.bottom-nav {
  position: absolute;
  right: 14px;
  bottom: 13px;
  left: 14px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  padding: 9px;
  border-radius: 28px;
  background: rgba(242, 243, 247, 0.9);
  box-shadow: 0 -10px 30px rgba(22, 24, 29, 0.08);
  backdrop-filter: blur(18px);
}

.bottom-nav button {
  display: grid;
  gap: 2px;
  place-items: center;
  min-height: 48px;
  border-radius: 20px;
  color: #20242b;
  background: transparent;
  font-size: 10px;
  font-weight: 800;
}

.bottom-nav span {
  font-size: 17px;
}

.bottom-nav button.active {
  color: #0f6fff;
  background: #fff;
  box-shadow: 0 8px 22px rgba(16, 24, 40, 0.08);
}

.detail-sheet {
  position: absolute;
  right: 12px;
  bottom: 86px;
  left: 12px;
  max-height: 56%;
  overflow-y: auto;
  padding: 20px;
  border: 1px solid rgba(16, 24, 40, 0.08);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 60px rgba(16, 24, 40, 0.24);
  backdrop-filter: blur(18px);
}

.close-detail {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 30px;
  height: 30px;
  border-radius: 999px;
  background: #f0f2f5;
  color: #555d68;
  font-size: 20px;
}

.detail-tags {
  display: flex;
  gap: 7px;
  padding-right: 36px;
}

.detail-tags span {
  padding: 4px 9px;
  border-radius: 999px;
  color: #0f6fff;
  background: rgba(15, 111, 255, 0.1);
  font-size: 11px;
  font-weight: 800;
}

.detail-sheet h2 {
  margin: 12px 34px 8px 0;
  color: #101114;
  font-size: 19px;
  line-height: 1.18;
}

.original-title {
  margin: 0 0 8px;
  color: #5e6570;
  font-size: 12px;
  font-weight: 700;
}

.detail-sheet p {
  color: #4c535e;
  font-size: 13px;
  line-height: 1.58;
}

.highlight-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0;
}

.highlight-grid span {
  padding: 8px 10px;
  border-radius: 14px;
  color: #242932;
  background: #f3f5f8;
  font-size: 12px;
  font-weight: 800;
}

.reason {
  border-left: 3px solid #ff2d55;
  padding-left: 10px;
}

.detail-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.detail-actions a,
.detail-actions button {
  flex: 1;
  padding: 11px 12px;
  border-radius: 16px;
  text-align: center;
  text-decoration: none;
  font-size: 13px;
  font-weight: 800;
}

.detail-actions a {
  color: #fff;
  background: #111318;
}

.detail-actions button {
  color: #ff2d55;
  background: rgba(255, 45, 85, 0.1);
}

.detail-actions button.active {
  color: #fff;
  background: #ff2d55;
}

.feature-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  max-width: 820px;
  margin: 24px auto 0;
}

.feature-strip div {
  display: grid;
  gap: 4px;
  padding: 18px;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 14px 34px rgba(16, 24, 40, 0.06);
}

.feature-strip strong {
  font-size: 26px;
  line-height: 1;
}

.feature-strip span {
  color: #6f7784;
  font-size: 13px;
  font-weight: 700;
}

@keyframes card-pop {
  from {
    transform: translateY(-10px) scale(0.98);
    opacity: 0.3;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

@media (max-width: 700px) {
  .arxiv-page {
    margin-top: -24px;
    padding-inline: 10px;
  }

  .hero-card {
    padding: 22px;
  }

  .phone-stage {
    min-height: 690px;
    border-radius: 28px;
  }

  .phone-frame {
    height: 650px;
  }

  .feature-strip {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
