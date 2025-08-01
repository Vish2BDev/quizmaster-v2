const { test, expect } = require('@playwright/test');

test.describe('Admin CRUD Operations', () => {
  let adminToken;

  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to dashboard
    await page.waitForURL('/admin/dashboard');
  });

  test.describe('Subject Management', () => {
    test('should create, read, update, and delete subjects', async ({ page }) => {
      // Navigate to Manage Subjects
      await page.goto('/admin/subjects');
      await page.waitForLoadState('networkidle');

      // CREATE: Add new subject
      await page.click('button:has-text("Add Subject")');
      await page.fill('input[placeholder="Subject Name"]', 'Test Subject');
      await page.fill('textarea[placeholder="Subject Description"]', 'Test Description');
      await page.click('button:has-text("Save")');
      
      // Verify subject was created
      await expect(page.locator('text=Test Subject')).toBeVisible();

      // UPDATE: Edit the subject
      await page.click('button[title="Edit"]');
      await page.fill('input[placeholder="Subject Name"]', 'Updated Test Subject');
      await page.click('button:has-text("Save")');
      
      // Verify subject was updated
      await expect(page.locator('text=Updated Test Subject')).toBeVisible();

      // DELETE: Remove the subject
      await page.click('button[title="Delete"]');
      await page.click('button:has-text("Delete")');
      
      // Verify subject was deleted
      await expect(page.locator('text=Updated Test Subject')).not.toBeVisible();
    });
  });

  test.describe('Chapter Management', () => {
    test('should create, read, update, and delete chapters', async ({ page }) => {
      // Navigate to Manage Chapters
      await page.goto('/admin/chapters');
      await page.waitForLoadState('networkidle');

      // CREATE: Add new chapter
      await page.click('button:has-text("Add Chapter")');
      await page.selectOption('select', { label: 'Mathematics' }); // Assuming Mathematics subject exists
      await page.fill('input[placeholder="Chapter Name"]', 'Test Chapter');
      await page.fill('textarea[placeholder="Chapter Description"]', 'Test Chapter Description');
      await page.click('button:has-text("Save")');
      
      // Verify chapter was created
      await expect(page.locator('text=Test Chapter')).toBeVisible();

      // UPDATE: Edit the chapter
      await page.click('button[title="Edit"]');
      await page.fill('input[placeholder="Chapter Name"]', 'Updated Test Chapter');
      await page.click('button:has-text("Save")');
      
      // Verify chapter was updated
      await expect(page.locator('text=Updated Test Chapter')).toBeVisible();

      // DELETE: Remove the chapter
      await page.click('button[title="Delete"]');
      await page.click('button:has-text("Delete")');
      
      // Verify chapter was deleted
      await expect(page.locator('text=Updated Test Chapter')).not.toBeVisible();
    });
  });

  test.describe('Quiz Management', () => {
    test('should create, read, update, and delete quizzes', async ({ page }) => {
      // Navigate to Manage Quizzes
      await page.goto('/admin/quizzes');
      await page.waitForLoadState('networkidle');

      // CREATE: Add new quiz
      await page.click('button:has-text("Add Quiz")');
      await page.selectOption('select[name="chapter"]', { index: 1 }); // Select first available chapter
      await page.fill('input[placeholder="Quiz Title"]', 'Test Quiz');
      await page.fill('textarea[placeholder="Quiz Description"]', 'Test Quiz Description');
      await page.fill('input[type="number"]', '10'); // Duration
      await page.click('button:has-text("Save")');
      
      // Verify quiz was created
      await expect(page.locator('text=Test Quiz')).toBeVisible();

      // UPDATE: Edit the quiz
      await page.click('button[title="Edit"]');
      await page.fill('input[placeholder="Quiz Title"]', 'Updated Test Quiz');
      await page.click('button:has-text("Save")');
      
      // Verify quiz was updated
      await expect(page.locator('text=Updated Test Quiz')).toBeVisible();

      // DELETE: Remove the quiz
      await page.click('button[title="Delete"]');
      await page.click('button:has-text("Delete")');
      
      // Verify quiz was deleted
      await expect(page.locator('text=Updated Test Quiz')).not.toBeVisible();
    });
  });

  test.describe('Question Management', () => {
    test('should create, read, update, and delete questions', async ({ page }) => {
      // Navigate to Manage Questions
      await page.goto('/admin/questions');
      await page.waitForLoadState('networkidle');

      // CREATE: Add new question
      await page.click('button:has-text("Add Question")');
      await page.selectOption('select[name="quiz"]', { index: 1 }); // Select first available quiz
      await page.fill('textarea[placeholder="Question Text"]', 'What is 2 + 2?');
      await page.fill('input[placeholder="Option A"]', '3');
      await page.fill('input[placeholder="Option B"]', '4');
      await page.fill('input[placeholder="Option C"]', '5');
      await page.fill('input[placeholder="Option D"]', '6');
      await page.selectOption('select[name="correct_answer"]', 'B');
      await page.click('button:has-text("Save")');
      
      // Verify question was created
      await expect(page.locator('text=What is 2 + 2?')).toBeVisible();

      // UPDATE: Edit the question
      await page.click('button[title="Edit"]');
      await page.fill('textarea[placeholder="Question Text"]', 'What is 3 + 3?');
      await page.fill('input[placeholder="Option B"]', '6');
      await page.click('button:has-text("Save")');
      
      // Verify question was updated
      await expect(page.locator('text=What is 3 + 3?')).toBeVisible();

      // DELETE: Remove the question
      await page.click('button[title="Delete"]');
      await page.click('button:has-text("Delete")');
      
      // Verify question was deleted
      await expect(page.locator('text=What is 3 + 3?')).not.toBeVisible();
    });
  });

  test.describe('User Management', () => {
    test('should view and manage users', async ({ page }) => {
      // Navigate to Manage Users
      await page.goto('/admin/users');
      await page.waitForLoadState('networkidle');

      // Verify user list is displayed
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('th:has-text("Username")')).toBeVisible();
      await expect(page.locator('th:has-text("Email")')).toBeVisible();
      await expect(page.locator('th:has-text("Role")')).toBeVisible();

      // Test search functionality
      await page.fill('input[placeholder*="search"]', 'admin');
      await page.waitForTimeout(1000); // Wait for search results
      await expect(page.locator('text=admin@example.com')).toBeVisible();

      // Test role filter
      await page.selectOption('select[name="role"]', 'admin');
      await page.waitForTimeout(1000);
      await expect(page.locator('text=admin@example.com')).toBeVisible();
    });
  });

  test.describe('Admin Dashboard', () => {
    test('should display admin overview with statistics', async ({ page }) => {
      await page.goto('/admin/dashboard');
      await page.waitForLoadState('networkidle');

      // Verify dashboard elements
      await expect(page.locator('h1:has-text("Admin Dashboard")')).toBeVisible();
      
      // Check for statistics cards
      await expect(page.locator('text=Total Users')).toBeVisible();
      await expect(page.locator('text=Total Subjects')).toBeVisible();
      await expect(page.locator('text=Total Quizzes')).toBeVisible();
      await expect(page.locator('text=Total Questions')).toBeVisible();
    });
  });
});