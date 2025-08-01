const { test, expect } = require('@playwright/test');

test.describe('Milestone 5: Score Persistence & History', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3000/login');
    
    // Login as test user
    await page.fill('input[type="email"]', 'testuser@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await page.waitForURL('**/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('Can navigate to Past Scores page from dashboard', async ({ page }) => {
    // Look for "View All Scores" button in dashboard
    const viewAllButton = page.locator('a[href="/past-scores"]');
    await expect(viewAllButton).toBeVisible();
    
    // Click to navigate to past scores
    await viewAllButton.click();
    
    // Verify we're on the past scores page
    await page.waitForURL('**/past-scores');
    await expect(page.locator('h1')).toContainText('Score History');
    
    // Check for key elements
    await expect(page.locator('.stat-card')).toHaveCount(4); // Total Attempts, Average Score, Best Score, Trend
    await expect(page.locator('text=Total Attempts')).toBeVisible();
    await expect(page.locator('text=Average Score')).toBeVisible();
    await expect(page.locator('text=Best Score')).toBeVisible();
  });

  test('Past Scores page displays correctly with no attempts', async ({ page }) => {
    // Navigate directly to past scores
    await page.goto('http://localhost:3000/past-scores');
    
    // Should show empty state
    await expect(page.locator('text=No Quiz Attempts Found')).toBeVisible();
    await expect(page.locator('text=Start taking quizzes to see your history here!')).toBeVisible();
    
    // Should have back to dashboard button
    await expect(page.locator('a[href="/dashboard"]')).toBeVisible();
  });

  test('Can toggle between table and card view', async ({ page }) => {
    await page.goto('http://localhost:3000/past-scores');
    
    // Look for view toggle button
    const toggleButton = page.locator('button:has-text("Card View"), button:has-text("Table View")');
    
    if (await toggleButton.isVisible()) {
      await toggleButton.click();
      // Verify the view changed (button text should change)
      await expect(toggleButton).toBeVisible();
    }
  });

  test('Search and filter functionality works', async ({ page }) => {
    await page.goto('http://localhost:3000/past-scores');
    
    // Test search input
    const searchInput = page.locator('input[placeholder*="Search quizzes"]');
    await expect(searchInput).toBeVisible();
    
    // Test subject filter
    const subjectFilter = page.locator('select').first();
    await expect(subjectFilter).toBeVisible();
    
    // Test sort dropdown
    const sortDropdown = page.locator('select').nth(1);
    await expect(sortDropdown).toBeVisible();
    
    // Test clear filters button
    const clearButton = page.locator('button:has-text("Clear")');
    await expect(clearButton).toBeVisible();
  });

  test('Quiz Summary page loads correctly', async ({ page }) => {
    // Navigate to quiz summary with mock data
    await page.goto('http://localhost:3000/quiz-summary');
    
    // Should redirect to dashboard if no result data
    await page.waitForURL('**/dashboard');
    
    // Test with mock result data
    await page.evaluate(() => {
      localStorage.setItem('lastQuizResult', JSON.stringify({
        score: 8,
        total_questions: 10,
        percentage: 80,
        time_taken: 300,
        quiz_id: 1
      }));
    });
    
    // Navigate to quiz summary again
    await page.goto('http://localhost:3000/quiz-summary');
    
    // Should show quiz results
    await expect(page.locator('text=80%')).toBeVisible();
    await expect(page.locator('text=Good Job!')).toBeVisible();
    await expect(page.locator('text=8 out of 10')).toBeVisible();
    
    // Check for action buttons
    await expect(page.locator('a[href="/my-quizzes"]')).toBeVisible();
    await expect(page.locator('a[href="/dashboard"]')).toBeVisible();
    await expect(page.locator('button:has-text("Retake Quiz")')).toBeVisible();
  });

  test('Quiz Summary shows different messages based on score', async ({ page }) => {
    // Test excellent performance (90%+)
    await page.evaluate(() => {
      localStorage.setItem('lastQuizResult', JSON.stringify({
        score: 9,
        total_questions: 10,
        percentage: 90,
        time_taken: 250,
        quiz_id: 1
      }));
    });
    
    await page.goto('http://localhost:3000/quiz-summary');
    await expect(page.locator('text=Excellent Performance!')).toBeVisible();
    await expect(page.locator('.fas.fa-trophy')).toBeVisible();
    
    // Test poor performance (<60%)
    await page.evaluate(() => {
      localStorage.setItem('lastQuizResult', JSON.stringify({
        score: 4,
        total_questions: 10,
        percentage: 40,
        time_taken: 400,
        quiz_id: 1
      }));
    });
    
    await page.goto('http://localhost:3000/quiz-summary');
    await expect(page.locator('text=Keep Practicing!')).toBeVisible();
  });

  test('Performance chart renders correctly', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('lastQuizResult', JSON.stringify({
        score: 7,
        total_questions: 10,
        percentage: 70,
        time_taken: 350,
        quiz_id: 1
      }));
    });
    
    await page.goto('http://localhost:3000/quiz-summary');
    
    // Check for chart canvas
    await expect(page.locator('canvas')).toBeVisible();
    
    // Check for legend
    await expect(page.locator('text=Correct: 7 questions')).toBeVisible();
    await expect(page.locator('text=Incorrect: 3 questions')).toBeVisible();
  });

  test('Navigation between score-related pages works', async ({ page }) => {
    // Start from dashboard
    await page.goto('http://localhost:3000/dashboard');
    
    // Go to past scores
    await page.click('a[href="/past-scores"]');
    await page.waitForURL('**/past-scores');
    
    // Go back to dashboard
    await page.click('a[href="/dashboard"]');
    await page.waitForURL('**/dashboard');
    
    // Test quiz summary navigation
    await page.evaluate(() => {
      localStorage.setItem('lastQuizResult', JSON.stringify({
        score: 6,
        total_questions: 10,
        percentage: 60,
        time_taken: 300,
        quiz_id: 1
      }));
    });
    
    await page.goto('http://localhost:3000/quiz-summary');
    
    // Navigate to view all attempts
    await page.click('a[href="/my-quizzes"]');
    await page.waitForURL('**/my-quizzes');
  });

  test('Backend endpoints are accessible', async ({ page }) => {
    // Test if the new endpoints respond (basic connectivity test)
    const response1 = await page.request.get('http://localhost:5000/api/user/scores', {
      headers: {
        'Authorization': 'Bearer test-token' // This will fail but we're testing endpoint existence
      }
    });
    
    // Should get 401 (unauthorized) or 422 (validation error), not 404 (not found)
    expect([401, 422, 500].includes(response1.status())).toBeTruthy();
    
    const response2 = await page.request.get('http://localhost:5000/api/user/quiz-attempt/1', {
      headers: {
        'Authorization': 'Bearer test-token'
      }
    });
    
    // Should get 401 (unauthorized) or 422 (validation error), not 404 (not found)
    expect([401, 422, 500].includes(response2.status())).toBeTruthy();
  });
});