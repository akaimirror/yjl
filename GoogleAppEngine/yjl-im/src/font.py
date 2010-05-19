import datetime
import os
import os.path

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class FontFile(webapp.RequestHandler):

  # Chromium don't use fonts with text/html as we want.
  EXT_TYPES = {
      '.otf': 'application/x-font-otf',
      '.ttf': 'application/x-font-ttf',
      '.eot': 'application/vnd.ms-fontobject',
      '.svg': 'image/svg+xml',
      '.js': 'application/x-javascript',
      '.woff': 'application/octet-stream',
      }

  def get(self, fontpath):

    fontpath = os.path.normpath(fontpath)
    # Does someone try to get other files?
    if fontpath.startswith('.') or fontpath.startswith('/'):
      self.error(403)
      return

    # Is requested file a font file?
    ext = os.path.splitext(fontpath)[1]
    if ext not in FontFile.EXT_TYPES.keys():
      self.error(403)
      return

    fontpath = 'font/%s' % fontpath
    # Does this font exist?
    if not os.path.exists(fontpath):
      self.error(404)
      return

    if 'Origin' not in self.request.headers:
      self.response.headers.add_header('Access-Control-Allow-Origin', 'http://www.yjl.im')
    elif os.environ['SERVER_NAME'] == 'localhost' or \
        self.request.headers['Origin'] in ['http://www.yjl.im', 'http://blog.yjl.im']:
      self.response.headers.add_header('Access-Control-Allow-Origin', self.request.headers['Origin'])
    else:
      self.response.headers.add_header('Access-Control-Allow-Origin', 'http://www.yjl.im')
      self.error(403)
      return
    
    self.response.headers['Content-Type'] = FontFile.EXT_TYPES[ext]
    
    expires = datetime.datetime.utcnow() + datetime.timedelta(365)
    self.response.headers.add_header('Expires', expires.strftime("%d %b %Y %H:%M:%S GMT"))
    self.response.headers['Cache-Control'] = 'public, max-age=%d' % (86400 * 365)
    
    f = open(fontpath)
    self.response.out.write(f.read())
    f.close()

  def head(self, fontpath):
    
    pass

application = webapp.WSGIApplication([
    ('/font/(.*)', FontFile),
    ],
    debug=True)


def main():

  run_wsgi_app(application)


if __name__ == "__main__":
  main()
