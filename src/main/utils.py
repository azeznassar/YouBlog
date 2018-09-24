def make_summary(posts):
    for p in posts:
        p.content = p.content[:60] + '...'
        p.content = " ".join(p.content.splitlines())
        