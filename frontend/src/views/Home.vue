<template>
  <div class="page">
    <div class="hero">
      <h1>WIKIIO</h1>
      <p>MediaWiki数据分析与评分平台</p>
      <div class="buttons">
        <a href="/register" class="btn-primary">立即注册</a>
        <a href="/login" class="btn-secondary">登录</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ffffff 0%, #DEDEDE 100%);
}
.hero { text-align: center; color: black; }
h1 { font-size: 3rem; margin-bottom: 1rem; }
p { font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9; }
.buttons { display: flex; gap: 1rem; justify-content: center; }
.btn-primary {
  padding: 0.8rem 2rem;
  background: rgb(54, 54, 54);
  color: #DEDEDE;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
}
.btn-secondary {
  padding: 0.8rem 2rem;
  border: 2px solid rgb(54, 54, 54);
  color: black;
  border-radius: 4px;
  text-decoration: none;
}
</style>