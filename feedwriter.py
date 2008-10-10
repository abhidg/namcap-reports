#!/usr/bin/python

import time

class FeedError(Exception): pass

def escape_xml(s):
	"""Escape special characters in XML."""
	chars = { "<" : "lt",
	          ">" : "gt",
	          "&" : "amp",
	          '"' : "quot",
	          "'" : "apos" }
	cs = []
	for c in s:
		if chars.has_key(c):
			cs.append("&" + chars[c] + ";")
		else:
			cs.append(c)
	return "".join(cs)

def wrap(name, value):
	if value is None:
		return ""
	else:
		return "<" + name + ">" + escape_xml(value).encode("UTF-8") + "</" + name + ">\n"

class Channel:
	"""A summary of a syndicated site."""

	def __init__(self, title, link, description):
		self.title = title
		self.link = link
		self.description = description
		self.items = []

	def add_item(self, *args, **keywords):
		"""Add an item to the feed. The arguments to this method
		   are the same as for the Item constructor."""
		self.items.append(Item(*args, **keywords))

	def rss2(self):
		"""Return the RSS 2.0 representation of this feed."""
		bits = []
		bits.append('<?xml version="1.0" encoding="UTF-8"?>\n')
		bits.append('<rss version="2.0">\n')
		bits.append('<channel>\n')
		bits.append(wrap("title", self.title))
		bits.append(wrap("link", self.link))
		bits.append(wrap("description", self.description))
		for item in self.items:
			bits.append('<item>\n')
			bits.append(wrap("title", item.title))
			bits.append(wrap("link", item.link))
			bits.append(wrap("description", item.description))
			if item.pubDate is not None:
				d = item.pubDate
				if type(d) is not tuple and type(d) is not time.struct_time:
					d = time.gmtime(d)
				s = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
				                  d)
				bits.append(wrap("pubDate", s))
			bits.append('</item>\n')
		bits.append('</channel>\n</rss>\n')
		return "".join(bits)

class Item:
	"""An item in a syndication feed."""

	def __init__(self, title = None, link = None, description = None, pubDate = None):
		if title is None and description is None:
			raise FeedError("Item must have either title or description")
		self.title = title
		self.link = link
		self.description = description
		self.pubDate = pubDate

if __name__ == "__main__":
	c = Channel(title = "Test Stuff", link = "http://teststuff.example.com/", description = "Some test items for feedwriter")
	c.add_item(title = "Title only")
	try:
		c.add_item(link = "http://example.com/")
	except FeedError:
		pass
	else:
		raise "Expected exception here"
	c.add_item(title = "All of them", link = "http://example.com/", description = "Here's some stuff complete with <strong>embedded HTML</strong>.", pubDate = time.time())
	print c.rss2()

