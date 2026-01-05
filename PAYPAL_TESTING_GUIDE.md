# PayPal Subscription Testing Guide

## ✅ Pre-Testing Checklist

### 1. PayPal Sandbox Setup
- [ ] Created PayPal Developer account at https://developer.paypal.com/
- [ ] Created REST API App and copied Client ID & Secret
- [ ] Created subscription plan and copied Plan ID (starts with `P-`)
- [ ] Have sandbox BUYER account credentials (for testing payments)
- [ ] Have sandbox BUSINESS account credentials (merchant account)

### 2. Environment Configuration
- [ ] Updated `.env` with PayPal credentials:
  ```bash
  PAYPAL_MODE=sandbox
  PAYPAL_CLIENT_ID=YOUR_CLIENT_ID
  PAYPAL_CLIENT_SECRET=YOUR_SECRET
  PAYPAL_PRO_PLAN_ID=P-YOUR_PLAN_ID
  ```
- [ ] Backend server restarted after `.env` changes
- [ ] Frontend is running on http://localhost:3000
- [ ] Backend is running on http://localhost:8000

### 3. Test User Setup
- [ ] Have a test user account registered in your app
- [ ] User has uploaded a resume
- [ ] User currently on Free plan (0/3 or less resumes used)

---

## 🧪 Test Scenarios

### Test 1: Usage Limit & Modal

**Goal**: Verify subscription modal appears when limit is reached

**Steps**:
1. Login to app (http://localhost:3000/login)
2. Navigate to Adzuna Workflow (`/dashboard/adzuna`)
3. Search for jobs (e.g., "Data Engineer")
4. Select a job
5. Choose resume (profile or upload)
6. Click "Use This Resume →"
7. **Generate resume #1** ✅
8. Repeat steps 3-7 for **resume #2** ✅
9. Repeat steps 3-7 for **resume #3** ✅
10. Repeat steps 3-7 for **resume #4** 🚫

**Expected Results**:
- ✅ Resumes 1-3 generate successfully
- ✅ On attempt #4, subscription modal appears
- ✅ Modal shows: "Monthly Limit Reached"
- ✅ Modal shows: "3 / 3" resumes used
- ✅ Modal shows reset date
- ✅ "Upgrade to Pro →" button visible
- ✅ "Maybe Later" button works (closes modal)

**Check Backend Logs**:
```
[ADZUNA] Checking usage limits...
[ADZUNA] Usage check passed: 2 resume(s) remaining this month
```

Then on 4th attempt:
```
[ADZUNA] Checking usage limits...
INFO: 127.0.0.1 - "POST /api/generation/adzuna HTTP/1.1" 403 Forbidden
```

---

### Test 2: Subscription Page

**Goal**: Verify subscription page displays correctly

**Steps**:
1. In subscription modal, click **"Upgrade to Pro →"**
2. Should redirect to `/subscription`

**Expected Results**:
- ✅ Page loads successfully
- ✅ "Current Usage" card shows:
  - Plan: FREE
  - Resumes: 3 / 3
  - Next Reset: [date]
- ✅ Free plan card (left side) shows "Current Plan" badge
- ✅ Pro plan card (right side) highlighted with gradient
- ✅ Pro benefits listed (unlimited, Adzuna, etc.)
- ✅ "Upgrade to Pro →" button visible
- ✅ FAQ section visible at bottom

---

### Test 3: PayPal Subscription Creation

**Goal**: Test full PayPal integration flow

**Steps**:
1. On `/subscription` page, click **"Upgrade to Pro →"**
2. Watch browser console and network tab

**Expected Results**:
- ✅ API request to `/api/subscription/create-pro`
- ✅ Backend creates subscription in PayPal
- ✅ Response contains `approval_url`
- ✅ Browser redirects to PayPal sandbox
- ✅ PayPal page shows:
  - "Resume Builder Pro"
  - "$9.99 USD / Month"
  - Login form

**Check Backend Logs**:
```
[SUBSCRIPTION] Creating subscription for user...
INFO: 127.0.0.1 - "POST /api/subscription/create-pro HTTP/1.1" 200 OK
```

**Check Database**:
```bash
sqlite3 resume_builder.db "SELECT plan_type, status FROM subscriptions WHERE plan_type='pro';"
# Should show: pro|pending
```

---

### Test 4: PayPal Approval

**Goal**: Complete PayPal payment and activate subscription

**Steps**:
1. On PayPal page, **login with SANDBOX BUYER account**
   - Email: `sb-xxxxx@personal.example.com`
   - Password: (from sandbox accounts page)
2. Review subscription details
3. Click **"Agree & Subscribe"**
4. Wait for redirect back to app

**Expected Results**:
- ✅ PayPal shows subscription details
- ✅ After approval, redirects to `/subscription/success?subscription_id=I-XXXXX`
- ✅ Success page shows "Welcome to Pro! 🎉"
- ✅ Shows "Activating your subscription..." with spinner
- ✅ After 2 seconds, redirects to `/subscription`
- ✅ Subscription page now shows:
  - Plan: PRO
  - Resumes: X / ∞ (unlimited)
  - "Cancel Subscription" button visible

**Check Backend Logs**:
```
[SUBSCRIPTION] Activating subscription I-XXXXX...
INFO: 127.0.0.1 - "POST /api/subscription/activate HTTP/1.1" 200 OK
```

**Check Database**:
```bash
sqlite3 resume_builder.db "SELECT plan_type, status FROM subscriptions WHERE plan_type='pro';"
# Should show: pro|active
```

---

### Test 5: Unlimited Resume Generation

**Goal**: Verify Pro users have unlimited access

**Steps**:
1. After upgrading, go to Adzuna Workflow
2. Generate 4th resume
3. Generate 5th resume
4. Generate 6th resume

**Expected Results**:
- ✅ All resumes generate successfully
- ✅ No subscription modal appears
- ✅ No 403 errors
- ✅ Usage tracked but not enforced

**Check Backend Logs**:
```
[ADZUNA] Checking usage limits...
[ADZUNA] Usage check passed: Unlimited access
```

---

### Test 6: Subscription Cancellation

**Goal**: Test subscription cancellation flow

**Steps**:
1. Navigate to `/subscription`
2. Click **"Cancel Subscription"** button
3. Confirm cancellation in browser prompt
4. Wait for response

**Expected Results**:
- ✅ Confirmation dialog appears
- ✅ After confirming, API call to `/api/subscription/cancel`
- ✅ Success toast: "Subscription cancelled successfully"
- ✅ Page updates to show:
  - Plan: FREE
  - "Upgrade to Pro →" button visible again
- ✅ Subscription cancelled in PayPal

**Check Backend Logs**:
```
[SUBSCRIPTION] Cancelling subscription I-XXXXX...
INFO: 127.0.0.1 - "POST /api/subscription/cancel HTTP/1.1" 200 OK
```

**Check Database**:
```bash
sqlite3 resume_builder.db "SELECT plan_type, status FROM subscriptions;"
# Should show:
# pro|cancelled (old subscription)
# free|active (new subscription)
```

**Verify in PayPal**:
1. Login to sandbox.paypal.com with BUSINESS account
2. Go to Products & Services → Subscriptions
3. Find the subscription
4. Status should be "Cancelled"

---

### Test 7: Cancel During PayPal Approval

**Goal**: Test user cancelling before completing payment

**Steps**:
1. On `/subscription`, click "Upgrade to Pro →"
2. Redirected to PayPal
3. **Click "Cancel and return to Resume Builder"** (at bottom of PayPal page)
4. Watch for redirect

**Expected Results**:
- ✅ Redirects to `/subscription/cancel`
- ✅ Shows "Subscription Cancelled" message
- ✅ Shows "No charges were made"
- ✅ "Go to Dashboard" and "Try Again" buttons work
- ✅ User still on Free plan
- ✅ No charges in PayPal

---

## 🐛 Troubleshooting

### Issue: "PayPal API credentials not configured"

**Solution**: Check `.env` file has all required values:
```bash
grep PAYPAL .env
# Should show 4 lines (MODE, CLIENT_ID, SECRET, PLAN_ID)
```

### Issue: "Invalid client credentials"

**Solutions**:
1. Verify credentials are from **Sandbox** (not Live)
2. Check for extra spaces in `.env` file
3. Regenerate API credentials in PayPal Developer Dashboard

### Issue: "Plan not found" or "Invalid plan ID"

**Solutions**:
1. Verify Plan ID starts with `P-`
2. Check plan is **Active** in PayPal Dashboard
3. Ensure plan is for **Sandbox** mode

### Issue: Backend 403 error but no modal shows

**Solution**: Check frontend error handling in `AdzunaWorkflowPage.jsx`:
```javascript
if (error.response?.status === 403 && error.response?.data?.detail?.error === 'usage_limit_exceeded') {
  setShowSubscriptionModal(true);
}
```

### Issue: Subscription created but not activated

**Solutions**:
1. Check `/subscription/success` URL has `subscription_id` parameter
2. Verify `activate` endpoint is called (check network tab)
3. Check backend logs for activation errors

---

## 📊 Database Queries for Verification

### Check User's Subscriptions
```bash
sqlite3 resume_builder.db "
  SELECT u.email, s.plan_type, s.status, s.start_date, s.next_billing_date
  FROM users u
  JOIN subscriptions s ON u.id = s.user_id
  WHERE s.status = 'active';
"
```

### Check Usage Records
```bash
sqlite3 resume_builder.db "
  SELECT u.email, ur.month_year, ur.resumes_generated, ur.reset_date
  FROM users u
  JOIN usage_records ur ON u.id = ur.user_id
  WHERE ur.month_year = strftime('%Y-%m', 'now');
"
```

### Check All Subscriptions History
```bash
sqlite3 resume_builder.db "
  SELECT plan_type, status, paypal_subscription_id, created_at
  FROM subscriptions
  ORDER BY created_at DESC;
"
```

---

## 🎯 Success Criteria

All tests passed if:
- ✅ Free users limited to 3 resumes/month
- ✅ Subscription modal appears on 4th attempt
- ✅ PayPal integration works (create → approve → activate)
- ✅ Pro users have unlimited access
- ✅ Cancellation works (PayPal + database updated)
- ✅ No console errors during flow
- ✅ Database reflects current subscription status

---

## 📝 Notes

- **Sandbox Mode**: All testing uses fake money, no real charges
- **Sandbox Accounts**: Use PayPal-generated test accounts only
- **Webhook**: Not required for basic testing (only for production)
- **Reset**: To reset usage, delete records from `usage_records` table

---

## 🚀 Ready for Production?

Before going live:
1. Switch `.env` to `PAYPAL_MODE=live`
2. Get Live API credentials from PayPal
3. Create production subscription plan
4. Set up PayPal webhook pointing to your domain
5. Test with real PayPal account (your own)
6. Implement proper error logging
7. Add email notifications for subscriptions

---

**Happy Testing!** 🎉
