import { spawn } from "node:child_process"
import path from "node:path"

import { Plugin } from "@opencode/plugin"

interface RunSlopInput {
  path: string
}

interface RunSlopResult {
  stdout: string
  stderr: string
  exitCode: number
}

function runSlop(script: string, file: string, cwd: string): Promise<RunSlopResult> {
  return new Promise((resolve) => {
    const child = spawn("uv", ["run", "--no-active", script, file], {
      cwd,
      stdio: ["ignore", "pipe", "pipe"],
    })

    let stdout = ""
    let stderr = ""
    let spawnError: Error | undefined

    child.stdout.setEncoding("utf8")
    child.stderr.setEncoding("utf8")
    child.stdout.on("data", (chunk: string) => {
      stdout += chunk
    })
    child.stderr.on("data", (chunk: string) => {
      stderr += chunk
    })

    child.on("error", (error) => {
      spawnError = error
    })

    child.on("close", (code, signal) => {
      if (spawnError) {
        resolve({ stdout, stderr: stderr + spawnError.message, exitCode: 127 })
        return
      }
      if (code === null) {
        resolve({
          stdout,
          stderr: stderr + `process terminated by signal ${signal ?? "unknown"}`,
          exitCode: 1,
        })
        return
      }
      resolve({ stdout, stderr, exitCode: code })
    })
  })
}

export default Plugin.define({
  id: "sloperator.run-slop",
  async setup(ctx) {
    const directory = ctx.location.directory
    const script = path.join(directory, "sloperator.py")

    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description:
          "Run a SlopLang (.slop) program with Sloperator. Returns stdout, stderr, and exitCode as JSON.",
        input: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description:
                "Path to the .slop file to run, relative to the project directory or absolute.",
            },
          },
          required: ["path"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const file = path.resolve(directory, (input as RunSlopInput).path)
          const result = await runSlop(script, file, directory)
          return { content: JSON.stringify(result) }
        },
      })
    })
  },
})
