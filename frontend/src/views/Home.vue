<template>
  <div class="hero-section">
    <div class="container">
      <div class="row align-items-center min-vh-100">
        <div class="col-lg-6">
          <h1 class="display-4 fw-bold mb-4">
            Welcome to Quiz Master V2
          </h1>
          <p class="lead mb-4">
            Test your knowledge with our interactive quiz platform. 
            Track your progress, compete with others, and master new subjects!
          </p>
          <div class="d-grid gap-2 d-md-flex">
            <QmBtn 
              variant="primary" 
              size="large" 
              @click="$router.push('/register')"
              class="me-md-2"
            >
              Get Started
            </QmBtn>
            <QmBtn 
              variant="outline" 
              size="large" 
              @click="$router.push('/login')"
            >
              Login
            </QmBtn>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="text-center">
            <i class="fas fa-graduation-cap hero-icon" style="font-size: 15rem;"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="features-section py-5 bg-light">
    <div class="container">
      <h2 class="text-center mb-5">Why Choose Quiz Master V2?</h2>
      <div class="row">
        <div class="col-md-4 mb-4">
          <QmCard class="h-100 text-center feature-card">
            <i class="fas fa-clock text-primary mb-3" style="font-size: 3rem;"></i>
            <h5 class="card-title">Real-time Quizzes</h5>
            <p class="card-text">Take timed quizzes with instant feedback and scoring.</p>
          </QmCard>
        </div>
        <div class="col-md-4 mb-4">
          <QmCard class="h-100 text-center feature-card">
            <i class="fas fa-chart-line text-success mb-3" style="font-size: 3rem;"></i>
            <h5 class="card-title">Performance Analytics</h5>
            <p class="card-text">Track your progress with detailed performance charts and reports.</p>
          </QmCard>
        </div>
        <div class="col-md-4 mb-4">
          <QmCard class="h-100 text-center feature-card">
            <i class="fas fa-users text-info mb-3" style="font-size: 3rem;"></i>
            <h5 class="card-title">Multi-user Platform</h5>
            <p class="card-text">Admin and user roles with comprehensive quiz management.</p>
          </QmCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import QmBtn from '@/components/atoms/QmBtn.vue'
import QmCard from '@/components/atoms/QmCard.vue'

export default {
  name: 'Home',
  components: {
    QmBtn,
    QmCard
  }
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, 
    #1E3A8A 0%, 
    #3B82F6 25%, 
    #0EA5E9 50%, 
    #06B6D4 75%, 
    #0891B2 100%);
  color: white;
  position: relative;
  overflow: hidden;
  margin-top: -76px;
  padding-top: 76px;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.08) 0%, transparent 50%),
    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
  opacity: 0.4;
}

.hero-section::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(180deg, 
    transparent 0%, 
    rgba(248, 250, 252, 0.1) 50%, 
    rgba(248, 250, 252, 0.3) 100%);
  pointer-events: none;
}

.hero-section .container {
  position: relative;
  z-index: 2;
}

.display-4 {
  font-family: 'Merriweather', serif;
  font-weight: 700;
  color: #FFFFFF;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  animation: fadeInUp 0.8s ease-out;
}

.lead {
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.hero-icon {
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  animation: float 3s ease-in-out infinite, fadeInUp 0.8s ease-out 0.4s both;
}

.btn {
  animation: fadeInUp 0.8s ease-out 0.6s both;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Features section enhancement */
.features-section {
  background: linear-gradient(135deg, 
    #FFFFFF 0%, 
    #F8FAFC 25%, 
    #F1F5F9 50%, 
    #F8FAFC 75%, 
    #FFFFFF 100%);
  border-top: 3px solid rgba(59, 130, 246, 0.1);
  position: relative;
}

.features-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    #3B82F6 25%, 
    #0EA5E9 50%, 
    #3B82F6 75%, 
    transparent 100%);
}

.features-section h2 {
  color: #1E3A8A;
  font-family: 'Merriweather', serif;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(30, 58, 138, 0.1);
}

.card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.1);
  box-shadow: 0 4px 20px rgba(30, 58, 138, 0.08);
  transition: all 0.3s ease;
  border-radius: 16px;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(30, 58, 138, 0.15);
  border-color: rgba(59, 130, 246, 0.2);
}

.card-title {
  color: #1E3A8A;
  font-weight: 600;
}

.card-text {
  color: #64748B;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.lead {
  font-size: 1.25rem;
  line-height: 1.6;
  color: #E0E7FF;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: #0EA5E9;
  border: none;
  padding: 12px 32px;
  font-weight: 600;
  border-radius: 50px;
  color: white;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-primary:hover {
  background: #2563EB;
  transform: scale(1.05);
  color: white;
}

.btn-outline-secondary {
  border: 1px solid #93C5FD;
  color: #93C5FD;
  background: transparent;
  padding: 12px 32px;
  font-weight: 600;
  border-radius: 50px;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-outline-secondary:hover {
  background: #93C5FD;
  color: #1E3A8A;
  transform: scale(1.05);
  border-color: #93C5FD;
}

.hero-icon {
  color: #BFDBFE;
  filter: drop-shadow(0 4px 8px rgba(191, 219, 254, 0.3));
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.features-section {
  background: #F8FAFC;
  position: relative;
}

.features-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(180deg, #3B82F6 0%, transparent 100%);
  opacity: 0.1;
}

.features-section h2 {
  font-family: 'Merriweather', serif;
  font-weight: 700;
  color: #1E3A8A;
  position: relative;
  z-index: 2;
}

/* Feature card styling for QmCard components */
.feature-card {
  border: none;
  border-radius: 20px;
  box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  background: white;
  overflow: hidden;
  position: relative;
  padding: 2rem;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3B82F6, #0EA5E9);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

/* Legacy card styles for backward compatibility */
.card {
  border: none;
  border-radius: 20px;
  box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  background: white;
  overflow: hidden;
  position: relative;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3B82F6, #0EA5E9);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.card:hover::before {
  transform: scaleX(1);
}

.card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.card-body {
  padding: 2rem;
  position: relative;
  z-index: 2;
}

.card-title {
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  color: #1E3A8A;
  margin-bottom: 1rem;
}

.card-text {
  color: #64748B;
  line-height: 1.6;
}

.fas.fa-clock {
  color: #3B82F6;
}

.fas.fa-chart-line {
  color: #22C55E;
}

.fas.fa-users {
  color: #0EA5E9;
}

.text-primary {
  color: #3B82F6 !important;
}

.text-success {
  color: #22C55E !important;
}

.text-info {
  color: #0EA5E9 !important;
}
</style>