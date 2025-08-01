const { test, expect } = require('@playwright/test');

test.describe('Debug Login Page', () => {
  test('Check what loads on login page', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Wait for page to load
    await page.waitForTimeout(3000);
    
    // Take a screenshot
    await page.screenshot({ path: 'debug-login-page.png', fullPage: true });
    
    // Check page title
    const title = await page.title();
    console.log('Page title:', title);
    
    // Check page URL
    const url = page.url();
    console.log('Current URL:', url);
    
    // Check if login form exists
    const loginForm = await page.locator('form').count();
    console.log('Number of forms found:', loginForm);
    
    // Check for username field
    const usernameField = await page.locator('#username').count();
    console.log('Username field found:', usernameField > 0);
    
    // Check for any input fields
    const inputFields = await page.locator('input').count();
    console.log('Total input fields:', inputFields);
    
    // Get page content
    const content = await page.content();
    console.log('Page contains "Login":', content.includes('Login'));
    console.log('Page contains "username":', content.includes('username'));
    
    // Check for any error messages
    const errorElements = await page.locator('.alert, .error, .warning').count();
    console.log('Error elements found:', errorElements);
  });
});