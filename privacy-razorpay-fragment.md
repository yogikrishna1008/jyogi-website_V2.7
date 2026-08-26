# Deferred privacy fragment — Razorpay disclosure (merge during/after R2)

**Do not publish standalone. Do not re-date `privacy.html` on its own for this.**

Reason (Genie revision #9): the live `privacy.html` still contains R0 logging/retention
statements that the approved R2 plan will correct (e.g. IP-hash handling, session-log
retention, "what we do not collect"). Publishing a freshly dated policy that adds the
Razorpay section while leaving those claims uncorrected would ship a policy that is
internally inconsistent with R2. This fragment is therefore held until it can be merged
in the same pass as the R2 corrections, and the "Last updated" date bumped once, then.

## What to change at merge time

1. In the section 2 data table, add these two rows:

```html
<tr><td>Name, email, phone</td><td>Process payment &amp; verify a booking (via Razorpay)</td><td>Held by Razorpay; not stored in a Jyogi database</td></tr>
<tr><td>Payment method, amount, status, transaction ID</td><td>Confirm payment, issue receipts, handle refunds</td><td>Held by Razorpay; Jyogi accesses limited transaction records only</td></tr>
```

2. Reword the "What we do NOT collect" paragraph so the payment claim is no longer false:

```html
<p>We do not collect Aadhaar numbers or any government-issued ID. We do not create
user accounts. We do not use cookies for tracking or advertising. Payment details
(see the Payments section) are handled by our payment processor, not stored by Jyogi.</p>
```

3. Insert this new section (place and renumber consistently with the R2-corrected policy):

```html
<h2>Payments (Razorpay)</h2>
<p>Paid consultations and reports are processed by <strong>Razorpay</strong>, a
third-party payment processor. When you pay, Razorpay may process your name, email,
phone number, payment method category, payment amount, payment status, transaction
identifier, and receipt/settlement data in order to complete the transaction.</p>
<p>Full card and UPI credentials are entered on Razorpay's secure checkout and are
handled entirely by Razorpay. <strong>Jyogi does not receive or store your full card
or UPI credentials.</strong> Jyogi may access limited transaction records (such as
payment status, amount and transaction identifier) and uses them only to verify your
booking, issue receipts, process refunds, and provide support.</p>
<p>Payment verification at Jyogi is <strong>manual</strong>: reaching a payment
success page is not by itself proof or confirmation of payment. Razorpay's privacy
policy: <a href="https://razorpay.com/privacy" target="_blank" rel="noopener">razorpay.com/privacy</a>.
See our <a href="/refund-policy.html">Refund &amp; Cancellation Policy</a> for refund terms.</p>
```

## Applied revisions already baked into this fragment
- "third-party payment processor" (not "RBI-regulated payment aggregator") — revision #7.
- "Jyogi may access limited transaction records … does not store full card/UPI credentials" — revision #8.
- Internal links use explicit `.html` — revision #4.
