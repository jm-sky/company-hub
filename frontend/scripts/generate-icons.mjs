import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const iconsDir = path.join(__dirname, '../public/icons')

async function renderPng(svgName, outName, size) {
  const svg = await readFile(path.join(iconsDir, svgName))
  const png = await sharp(svg).resize(size, size).png().toBuffer()
  await writeFile(path.join(iconsDir, outName), png)
  console.log(`Wrote ${outName} (${size}x${size})`)
}

await mkdir(iconsDir, { recursive: true })
await renderPng('icon.svg', 'icon-192.png', 192)
await renderPng('icon.svg', 'icon-512.png', 512)
await renderPng('icon-maskable.svg', 'icon-maskable-512.png', 512)
