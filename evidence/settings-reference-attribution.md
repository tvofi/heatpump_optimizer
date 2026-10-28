
Control the attribution Claude Code adds to commits and pull requests and how it works with git.

### `attribution`

Customize the attribution Claude Code adds to git commits and pull requests. Commits get a [git trailer](https://git-scm.com/docs/git-interpret-trailers) such as `Co-Authored-By` by default; pull request descriptions get plain text. Set each part separately with the sub-keys below.

* **Scope**: [`Any file`](#scopes)
* **Type**: object with `commit` and `pr` strings and a `sessionUrl` Boolean, or `false` to hide all attribution. The `false` value requires Claude Code v2.1.281 or later; earlier versions reject it and [skip the whole user, project, or local settings file](/docs/en/settings.md#fix-a-broken-settings-file) that holds it
* **Default**: unset, so Claude Code uses the standard attribution shown under each sub-key

To hide all attribution, set `attribution` to `false`. In a settings file that earlier versions also read, set [`commit`](#attribution-commit) and [`pr`](#attribution-pr) to empty strings and [`sessionUrl`](#attribution-sessionurl) to `false` instead.

This example replaces the commit attribution, removes pull request attribution, and drops the session link:

```json settings.json theme={null}
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI <ai@example.com>",
    "pr": "",
    "sessionUrl": false
  }
}
```

Once you set `commit` or `pr`, Claude Code ignores the deprecated `includeCoAuthoredBy` setting and uses its default text for whichever of the two you left unset.

Claude Code tells Claude that your own instructions about attribution, such as a CLAUDE.md or [memory](/docs/en/memory.md) rule, take precedence over these commit and PR lines, unless the line is set in [managed settings](/docs/en/managed-settings.md).
### `attribution.commit`

Set the attribution text Claude Code adds to git commits, including any trailers. Set it to an empty string to hide commit attribution.

* **Scope**: [`Any file`](#scopes)
* **Type**: string
* **Default**: unset, so Claude Code adds `Co-Authored-By: <name> <noreply@anthropic.com>`. The name is the model in use when the commit is made, such as `Claude Sonnet 5`. When a [subagent](/docs/en/sub-agents.md) makes the commit, the trailer names the subagent's model.
  * When Claude Code recognizes the model as a Claude model but can't confirm its exact version, it writes `Claude` alone.
  * When it can't match the model ID to any Claude model, such as a third-party model served through a custom [`ANTHROPIC_BASE_URL`](/docs/en/env-vars), it writes `Claude Code`.

This example replaces the default trailer with a custom line and a custom `Co-Authored-By` trailer:

```json settings.json theme={null}
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI <ai@example.com>"
  }
}
```

### `attribution.pr`

Set the attribution text Claude Code adds to pull request descriptions. Set it to an empty string to hide pull request attribution.

* **Scope**: [`Any file`](#scopes)
* **Type**: string
* **Default**: unset, so Claude Code adds `🤖 Generated with [Claude Code](https://claude.com/claude-code)`

```json settings.json theme={null}
{
  "attribution": {
    "pr": ""
  }
}
```

### `attribution.sessionUrl`

Choose whether Claude Code appends the claude.ai session link when it commits or opens a pull request from a [cloud](/docs/en/claude-code-on-the-web.md) or [Remote Control](/docs/en/remote-control.md) session. Claude Code adds the link as a `Claude-Session` trailer on commits and as a link in pull request descriptions. Set it to `false` to omit the link.

* **Scope**: [`Any file`](#scopes)
* **Type**: Boolean
  * `true`: Claude Code appends the claude.ai session link when it commits or opens a pull request from a cloud or Remote Control session
  * `false`: Claude Code omits the link
* **Default**: `true`

```json settings.json theme={null}
{
  "attribution": {
    "sessionUrl": false
  }
}
```

## Hooks and automation
