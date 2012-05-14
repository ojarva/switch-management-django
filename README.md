Switch management
=================

This service offers centralized switch management interface for Dell PowerConnect 5448 switches (works probably with others supporting ssh too). At Futurice, we are using VLANs to separate guest network sockets and LAN. 
Earlier we physically moved cables between switches, but that was slow and error-prone procedure. Also, it made switch rack huge mess.

Installation
------------

* Django
* South

```
python manage.py syncdb
```

* This uses static files from cdn.futurice.com

License
-------

MIT license:

Copyright (C) 2011-2012 Futurice Ltd, Olli Jarva

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without 
limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.
