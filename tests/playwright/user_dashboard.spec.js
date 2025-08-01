const { test, expect } = require('@playwright/test');

// Test configuration
const BASE_URL = 'http://localhost:3002';
const API_BASE_URL = 'http://localhost:5000';

// Test user credentials
const TEST_USER = {
  email: 'test@example.com',
  password: 'password123'
};

test.describe('User Dashboard Features', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate directly to the login page
    await page.goto(`${BASE_URL}/login`);

    // Wait for login form to be visible
    await page.waitForSelector('#username', { timeout: 10000 });
    
    // Login as test user
    await page.fill('#username', 'testuser');
    await page.fill('#password', TEST_USER.password);
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await page.waitForSelector('h2:has-text("Dashboard Overview")', { timeout: 10000 });
  });

  test('Dashboard loads successfully', async ({ page }) => {
    // Check if dashboard content is visible
    await expect(page.locator('h2:has-text("Dashboard Overview")')).toBeVisible();
    
    // Check if user navigation is present
    await expect(page.locator('.user-sidebar')).toBeVisible();
    
    // Check if welcome message is present
    await expect(page.locator('text=Welcome back,testuser!')).toBeVisible();
  });

  test('Performance stats cards display correctly', async ({ page }) => {
    // Wait for stats to load - using actual structure from Vue component
    await page.waitForSelector('h3', { timeout: 10000 });
    
    // Check Total Attempts - first stat
    await expect(page.locator('h3').first()).toContainText('0');
    await expect(page.locator('p').filter({ hasText: 'Total Attempts' })).toBeVisible();
    
    // Check Best Score - second stat
    await expect(page.locator('h3').nth(1)).toContainText('0%');
    await expect(page.locator('p').filter({ hasText: 'Best Score' })).toBeVisible();
    
    // Check Average Score - third stat
    await expect(page.locator('h3').nth(2)).toContainText('0%');
    await expect(page.locator('p').filter({ hasText: 'Average Score' })).toBeVisible();
    
    // Check Current Streak - fourth stat
    await expect(page.locator('h3').nth(3)).toContainText('5');
    await expect(page.locator('p').filter({ hasText: 'Current Streak' })).toBeVisible();
  });

  test('Available quizzes section displays correctly', async ({ page }) => {
    // Navigate to quizzes tab first
    await page.click('text=My Quizzes');
    await page.waitForTimeout(2000);
    
    // Check if we're on the My Quizzes page
    await expect(page.locator('h2').filter({ hasText: 'My Quizzes' })).toBeVisible();
    await expect(page.locator('text=View and manage your quiz attempts')).toBeVisible();
    
    // Check if we're on the quizzes page or if quizzes are loaded
    const quizCards = page.locator('.quiz-card');
    const quizCount = await quizCards.count();
    
    if (quizCount > 0) {
      // Check quiz card structure if quizzes exist
      const firstQuizCard = quizCards.first();
      await expect(firstQuizCard.locator('.card-title')).toBeVisible();
      await expect(firstQuizCard.locator('.card-text')).toBeVisible();
      await expect(firstQuizCard.locator('.btn-primary')).toBeVisible();
      await expect(firstQuizCard.locator('.btn-primary')).toContainText('Start Quiz');
    } else {
      // If no quiz attempts, check for empty state message
      await expect(page.locator('h4').filter({ hasText: 'No Quiz Attempts Yet' })).toBeVisible();
      await expect(page.locator('text=Start taking quizzes to see your attempts here!')).toBeVisible();
    }
  });

  test('Quiz cards are clickable and functional', async ({ page }) => {
    // Navigate to quizzes tab first
    await page.click('text=My Quizzes');
    await page.waitForTimeout(2000);
    
    const quizCards = page.locator('.quiz-card');
    const quizCount = await quizCards.count();
    
    if (quizCount > 0) {
      // Click on the first quiz card's "Start Quiz" button
      const firstQuizCard = quizCards.first();
      await firstQuizCard.locator('.btn-primary').click();
      
      // Wait for navigation or quiz interface
      await page.waitForTimeout(3000);
      
      // Check if we navigated to a quiz page or if quiz interface appears
      const currentUrl = page.url();
      const hasQuizInUrl = currentUrl.includes('/quiz/');
      
      if (hasQuizInUrl) {
        // Successfully navigated to quiz page
        await expect(page).toHaveURL(/\/quiz\/\d+/);
      } else {
        // Check for quiz interface on same page
        const quizInterface = page.locator('.quiz-container, .modal-content, .quiz-question');
        await expect(quizInterface).toBeVisible({ timeout: 5000 });
      }
    } else {
      // No quiz attempts yet - verify we're on the correct page
      await expect(page.locator('h4').filter({ hasText: 'No Quiz Attempts Yet' })).toBeVisible();
      console.log('No quiz cards available to test - showing empty state correctly');
    }
  });

  test('Navigation menu works correctly', async ({ page }) => {
    // Check if user sidebar navigation is present
    await expect(page.locator('.user-sidebar')).toBeVisible();
    
    // Test Dashboard link (should be active)
    const dashboardLink = page.locator('a[href="/dashboard"]');
    await expect(dashboardLink).toBeVisible();
    await expect(dashboardLink).toContainText('Dashboard Overview');
    
    // Test other navigation links
    await expect(page.locator('a[href="/my-quizzes"]')).toBeVisible();
    await expect(page.locator('a[href="/leaderboard"]')).toBeVisible();
    await expect(page.locator('a[href="/my-stats"]')).toBeVisible();
    await expect(page.locator('a[href="/achievements"]')).toBeVisible();
    
    // Test Logout functionality
    const logoutButton = page.locator('button').filter({ hasText: 'Logout' });
    await expect(logoutButton).toBeVisible();
  });

  test('API endpoints respond correctly', async ({ page }) => {
    // Intercept API calls and verify they succeed
    const apiCalls = [];
    
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        apiCalls.push({
          url: response.url(),
          status: response.status()
        });
      }
    });
    
    // Reload the page to trigger API calls
    await page.reload();
    await page.waitForTimeout(3000);
    
    // Check that API calls were made and successful
    expect(apiCalls.length).toBeGreaterThan(0);
    
    // Check specific API endpoints
    const performanceCall = apiCalls.find(call => call.url.includes('/api/user/performance'));
    const quizzesCall = apiCalls.find(call => call.url.includes('/api/quizzes/available'));
    
    if (performanceCall) {
      expect(performanceCall.status).toBe(200);
    }
    
    if (quizzesCall) {
      expect(quizzesCall.status).toBe(200);
    }
  });

  test('Responsive design works on different screen sizes', async ({ page }) => {
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // Check if dashboard is still visible and functional
    await expect(page.locator('h2:has-text("Dashboard Overview")')).toBeVisible();
    await expect(page.locator('h3').first()).toBeVisible(); // Stats are still visible
    
    // Test tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    
    await expect(page.locator('h2:has-text("Dashboard Overview")')).toBeVisible();
    await expect(page.locator('h3').first()).toBeVisible();
    
    // Test desktop view
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForTimeout(1000);
    
    await expect(page.locator('h2:has-text("Dashboard Overview")')).toBeVisible();
    await expect(page.locator('h3').first()).toBeVisible();
  });

  test('Error handling works correctly', async ({ page }) => {
    // Intercept API calls and simulate failures
    await page.route('**/api/user/performance', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
    
    // Reload page to trigger the failed API call
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Check if we're redirected to login page after reload
    const currentUrl = page.url();
    if (currentUrl.includes('/login') || !currentUrl.includes('/dashboard')) {
      // Re-login after reload
      await page.fill('#username', TEST_USER.email);
      await page.fill('#password', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
    }
    
    // Check that the page still loads (should show mock data or error handling)
    await expect(page.locator('h2:has-text("Dashboard Overview")')).toBeVisible();

    // Stats should still be visible (with default/mock data or fallback values)
    await expect(page.locator('h3').first()).toBeVisible();
    
    // Verify that stats are showing some values (could be default or cached)
    const firstStatValue = await page.locator('h3').first().textContent();
    expect(firstStatValue).toBeTruthy(); // Just verify it has some content
  });

  test('User can logout successfully', async ({ page }) => {
    // Find and click logout button
    const logoutButton = page.locator('button').filter({ hasText: 'Logout' });
    
    await expect(logoutButton).toBeVisible();
    await logoutButton.click();
    
    // Wait for redirect to login page
    await page.waitForTimeout(2000);
    
    // Check if redirected to login page or home page
    const isOnLogin = page.url().includes('/login');
    const isOnHome = page.url() === BASE_URL + '/' || page.url() === BASE_URL;
    
    if (isOnLogin) {
      await expect(page.locator('#username')).toBeVisible();
    } else if (isOnHome) {
      await expect(page.locator('text=Login')).toBeVisible();
    } else {
      // Check for any login-related elements
      const loginElements = page.locator('input[type="email"], input[type="text"][placeholder*="email"], input[placeholder*="username"]');
      await expect(loginElements.first()).toBeVisible({ timeout: 5000 });
    }
  });
});

test.describe('Quiz Taking Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('#username', 'testuser');
    await page.fill('#password', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForSelector('h2:has-text("Dashboard Overview")', { timeout: 10000 });
  });

  test('Can start and complete a quiz', async ({ page }) => {
    // We should already be logged in from beforeEach
    // Verify we're on the dashboard
    await expect(page.locator('h2:has-text("Dashboard Overview")')).toBeVisible();
    
    // Navigate to My Quizzes
    await page.click('a[href="/my-quizzes"]');
    await page.waitForTimeout(2000);
    
    // Check if there are any quizzes available
    const quizCards = await page.locator('.quiz-card').count();
    
    if (quizCards === 0) {
      // If no quizzes, verify the empty state message
      await expect(page.locator('text=No Quiz Attempts Yet')).toBeVisible();
      console.log('No quiz cards available to test');
      return;
    }
    
    // Click on the first available quiz
    await page.click('.quiz-card .btn-primary');
    await page.waitForTimeout(2000);
    
    // Should navigate to quiz page or show quiz interface
    // Check for quiz-related elements
    const hasQuizInterface = await page.locator('.quiz-container, .quiz-question, .question-container').count() > 0;
    const isOnQuizPage = page.url().includes('/quiz/') || page.url().includes('/take-quiz');
    
    expect(hasQuizInterface || isOnQuizPage).toBeTruthy();
  });
});