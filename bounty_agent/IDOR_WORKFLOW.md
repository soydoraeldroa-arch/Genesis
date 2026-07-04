# Manual IDOR / Broken-Access-Control Workflow

This is a **human-driven** workflow, not an automated scan. IDOR (Insecure
Direct Object Reference) and broken access control are the highest-paying
common bug classes, and they are exactly the ones a scanner cannot find,
because "this returned HTTP 200" tells you nothing about whether the data
*should* have been visible to *this* account. You supply the judgment; this
doc gives you the process and a clean report template.

Nothing here runs a live authenticated session on your behalf. You drive the
requests from your own two test accounts; I help you reason about what to
vary and how to write it up.

## Hard rules (from the X/xAI program policy — stay inside these)

- Use **only test accounts you created**. Never touch a real user's data.
- The moment you can see data belonging to an account you don't control,
  **stop, screenshot, and report** — do not enumerate further, do not pull
  more records. "Accessing private information of other users ... will
  immediately disqualify the report."
- No automated high-volume ID enumeration — that trips the DoS/abuse line.
  A handful of manual requests proving the flaw is enough.

## Setup: two accounts

1. Register **Account A** and **Account B** as test accounts on the in-scope app.
2. In A, create/own an object (a post, a profile field, an uploaded file, an
   order, a message thread — whatever the app has). Note its identifier.
3. Log in as B. This is your "attacker" context.

## The core test

For every request that references an object by an identifier, ask:
**"Can Account B access Account A's object just by using A's identifier?"**

1. As Account A, capture a request that returns A's object. Note:
   - the URL / endpoint
   - the identifier and *where* it lives (path `/api/notes/4821`, query
     `?id=4821`, body `{"note_id":4821}`, or a header)
   - what a legitimate response looks like
2. Log in as Account B. Repeat the **exact same request**, but swap in A's
   identifier while using **B's session cookie/token**.
3. Read the response:
   - Returns **A's data** → **IDOR confirmed.** Stop and document.
   - `403 / 404 / empty` → access control is working here. Move on.

## Where to vary the identifier (checklist)

- [ ] Numeric IDs in the path (`/users/123`, `/orders/456`) — try ±1, and A's ID
- [ ] IDs in query strings (`?doc=...`, `?account=...`)
- [ ] IDs in JSON/form bodies (often missed — bodies get less validation)
- [ ] UUIDs/hashes — still test them; "unguessable" is not "authorized". If B can
      obtain A's UUID anywhere (a share link, a listing, an email), it's fair game.
- [ ] The HTTP method: does `GET /notes/{id}` 403 but `DELETE`/`PUT` /`PATCH` succeed?
- [ ] Mass-assignment: add a field you shouldn't control (`"role":"admin"`,
      `"owner_id":<A>`, `"verified":true`) to a request B *is* allowed to make.
- [ ] Second-order: B creates something referencing A's object id — does it leak
      A's data back on read?
- [ ] "Unlink"/removal of your own access, then re-access via direct id.

## Related access-control flaws worth the same 2-account test

- **Privilege escalation** — can a normal-role account hit an admin-only endpoint?
- **Tenant isolation** — in a multi-org app, can org B read org A's resources?
- **Function-level authz** — the UI hides a button; does the API still honor the
  call when you send it directly?

## When you get a hit — capture this, then bring it to me

Paste these (redact your own tokens/cookies):
1. The exact request as Account B (method, URL, relevant headers minus the raw
   session token, body).
2. The response proving you got Account A's data (the field(s) that are A's).
3. Which identifier you changed, and its original vs. swapped value.

I'll help you: confirm it's a real authz boundary crossing (not just public
data), gauge severity against the program's 5x5 matrix, and draft the report.

## Report template (IDOR)

```
# IDOR: [endpoint] exposes other users' [object type]

## Summary
The [METHOD] [endpoint] endpoint returns/modifies an object referenced by
[identifier] without verifying the authenticated user owns it. An attacker
authenticated as any user can access [object type] belonging to arbitrary
other users by supplying their [identifier].

## Steps to Reproduce
1. Register two accounts, A (victim) and B (attacker).
2. As A, create [object] — its id is `<A_ID>`. (Screenshot 1)
3. Log in as B. Send:
       [METHOD] [endpoint with <A_ID>]
       [minimal headers — with B's session]
4. Observe the response returns A's [object]: [the giveaway field]. (Screenshot 2)

## Impact
Any authenticated user can [read/modify/delete] any other user's [object type],
exposing [PII / private content / etc.]. [Note if no auth is even needed, or if
it enables account takeover / financial impact — that raises severity.]

## Proof of Concept
[request + response, tokens redacted]

## Remediation
Enforce an ownership/authorization check server-side: verify the authenticated
principal is permitted to act on the referenced object before returning it.
```

## Reminder

A confirmed IDOR is worth writing up carefully and slowly. One clean,
well-evidenced report beats ten noisy ones — and on this program, an
unverified automated-looking submission is an instant disqualifier.
