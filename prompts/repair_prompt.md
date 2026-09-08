The end-to-end test failed on its last step. Here is the failure:

Page doesn't contain 'This password reset link has already been used' but it's supposed to in command 'check that page contains "This password reset link has already been used"'
The specification requires that a password reset link works exactly
once. After it has been used to set a new password, reopening the same
link must show exactly:

    This password reset link has already been used

Fix the implementation so the test passes.

Scope: this failure only. Do not add link expiry, rate limiting,
email enumeration protection, CSRF tokens, or any other hardening. Do
not refactor unrelated code. Do not add tests.
