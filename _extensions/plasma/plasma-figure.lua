-- {{< plasma-figure figures/growth caption="..." width="80%" height="600px" >}}
--
-- A figure written by plasma_presentations.figure: in HTML the interactive Plotly figure
-- (figures/growth.json, inlined so the deck also works from file://), in Beamer and other
-- formats the static image (figures/growth.pdf, else figures/growth.png).

local PLOTLY = "https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.2/plotly.min.js"
local count = 0

local function str(value, default)
  if value == nil then
    return default
  end
  local text = pandoc.utils.stringify(value)
  if text == "" then
    return default
  end
  return text
end

local function document_dir()
  local input = quarto.doc.input_file
  if input == nil or input == "" then
    return "."
  end
  return pandoc.path.directory(input)
end

local function exists(path)
  local file = io.open(path, "r")
  if file ~= nil then
    file:close()
    return true
  end
  return false
end

local function read(path)
  local file = io.open(path, "r")
  local text = file:read("a")
  file:close()
  return text
end

local function escape_html(text)
  return (text:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function html_figure(stem, json, caption, width, height)
  count = count + 1
  local id = "plasma-figure-" .. count
  if count == 1 then
    quarto.doc.include_text("in-header", '<script src="' .. PLOTLY .. '"></script>')
  end
  local data = read(json):gsub("</", "<\\/")
  local html = '<figure class="plasma-figure" style="width: ' .. width .. ';">'
    .. '<div class="plasma-figure-plot" data-source="' .. id .. '-data" style="height: '
    .. height .. ';" role="img" aria-label="' .. escape_html(caption ~= "" and caption or stem)
    .. '"></div>'
    .. '<script type="application/json" id="' .. id .. '-data">' .. data .. "</script>"
  if caption ~= "" then
    html = html .. '<figcaption class="plasma-figure-caption">' .. escape_html(caption) .. "</figcaption>"
  end
  return pandoc.RawBlock("html", html .. "</figure>")
end

local function static_figure(stem, base, caption, width)
  local image = nil
  for _, suffix in ipairs({ ".pdf", ".png" }) do
    if exists(pandoc.path.join({ base, stem .. suffix })) then
      image = stem .. suffix
      break
    end
  end
  if image == nil then
    error("plasma-figure: neither " .. stem .. ".pdf nor " .. stem .. ".png exists next to the document")
  end
  -- a captioned pandoc.Figure from a shortcode trips Quarto's figure filters, so the caption
  -- is a paragraph of its own below the image
  local latex = quarto.doc.is_format("latex")
  local picture = pandoc.Image({}, image, "", { width = width })
  if latex then
    -- the width, at most 72 % of the frame's height (room for its title and the caption),
    -- in proportion
    local percent = width:match("^(%d+%.?%d*)%%$")
    local size = percent and string.format("%g\\linewidth", tonumber(percent) / 100) or width
    picture = pandoc.RawInline("latex", "\\centering\\includegraphics[width=" .. size
      .. ",height=0.72\\textheight,keepaspectratio]{" .. image .. "}")
  end
  local blocks = { pandoc.Para({ picture }) }
  if caption ~= "" then
    local text = pandoc.utils.blocks_to_inlines(pandoc.read(caption, "markdown").blocks)
    if latex then
      table.insert(text, 1, pandoc.RawInline("latex", "{\\centering\\footnotesize\\color{plasmamuted} "))
      table.insert(text, pandoc.RawInline("latex", "\\par}"))
      table.insert(blocks, pandoc.Para(text))
    else
      table.insert(blocks, pandoc.Para({ pandoc.Emph(text) }))
    end
  end
  return pandoc.Blocks(blocks)
end

return {
  ["plasma-figure"] = function(args, kwargs)
    local stem = str(args[1], nil)
    if stem == nil then
      error("plasma-figure: give the figure's path without suffix, e.g. {{< plasma-figure figures/growth >}}")
    end
    local caption = str(kwargs["caption"], "")
    local width = str(kwargs["width"], "100%")
    local height = str(kwargs["height"], "600px")
    local base = document_dir()
    local json = pandoc.path.join({ base, stem .. ".json" })
    if quarto.doc.is_format("html:js") and exists(json) then
      return html_figure(stem, json, caption, width, height)
    end
    return static_figure(stem, base, caption, width)
  end,
}
