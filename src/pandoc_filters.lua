function Header (h)
  if h.identifier ~= '' then
    local anchor_link = pandoc.Link(
      {},
      '#' .. h.identifier,
      '',
      {class = 'anchor'} -- attributes
    )
    h.content:insert(#h.content + 1, anchor_link)
    return h
  end
end
