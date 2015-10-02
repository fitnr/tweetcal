# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

README.rst: README.md
	pandoc $< -o $@

test:
	tweetcal archive -n data/js/tweets test.ics
	tweetcal stream -n --config sample-config.yaml --user your_username_here || :