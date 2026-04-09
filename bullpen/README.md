# `bullpen` - the plugin API for MLB-LED-Scoreboard

While the mlb-led-scoreboard project is primarily dedicated to showing baseball games, over the years
it has grown a few features and spin-offs for displaying other things. After all, there is that tragic
time between November and February where no baseball is played, so it might as well show _something_
during that time.

For the longest time, this project supported two additional screens. One showed divisional and wild card standings,
and the other a collection of headlines and the current time and weather. Various developers built their own displays
on top of our code, showing such information as [Disney Park wait times](https://github.com/jc214809/LightningLane-Live-LED) or
[NYC Subway statuses](github.com/WardBrian/mta-board).

`bullpen` is our framework to allow easier creation of these kinds of non-baseball-game displays.

If you build a plugin, please let us know about it!

## For users

We recommend reading the ["plugins" section of the top-level README](../README.md#plugins).

## For developers

A `bullpen`-compatible plugin is actually quite simple. Really, all that is
needed is to implement three classes conforming to a specific API -- a config
class, a data-storing class, and a renderer -- and define a function that is
exposed as
[a Python entrypoint](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata)
which returns those three. The `bullpen.api` module is fully type-hinted to assist in
writing these correctly.

For examples, see [`example-plugin`](./example-plugin/) here, and [`news`](../news/) and [`standings`](../standings/) in the top-level directory.


### The Config class

At construction, this is passed an object that includes some top-level configuration (like the user's preferred scrolling speed)
and a `plugin_config` dictionary, which contains the contents of the users `config.json`'s `plugins.PLUGINNAME` key.

No other requirements are put on this class. Consider doing any validation or preprocessing here, as it will be constructed
only one but accessed *many* times.

### The Data class

At construction, this is passed *your Config class from the previous section*.

There is only one required method, `update`, which can be used to update the data stored in your class. Note that
**you should assume `update()` will be called multiple times per second**. If you are doing something like
a web request in the update function, you absolutely must implement a check that some time has passed before
the last update, as our `news` and `standings` examples both illustrate.

`update` must return an `UpdateStatus` enum, which indicates if the request succeeded, failed, or was deferred. Failures
are shown as a red exclamation point on the board to let the user know there is a network issue.

### The Renderer class

This is the most complicated class of the three. At construction, it recieves *your Config class* as well
as classes that contain layout and color information from the user's configuration.

The first is `render`. Note that this method draws one single frame, and will be called multiple times in a row.
Do not put your own rendering loops inside this function.

`render` recieves, in order: your plugin's Data object, the Canvas object, the `graphics` module, and an integer with the current scrolling
text position. If scrolling text is used, it should return the position returned from that function, otherwise it can return None.

The second method is `wait_time`, which determines how long it will be between calls to `render` in seconds. The user's configured value of `scrolling_speed`
should be used if scrolling text is needed, otherwise a value such as 1 second is reasonable.

There are also two optional methods:

- `can_render` takes in your Data class and returns a bool. If this function returns false, the plugin will be skipped in that rotation.
- `reset` is called when your board is being rotated away from at the end of its turn, and can be used to reset any internal state

### Registering your plugin

To actually have the scoreboard software register your plugin, you need to define a function
(that we usually call `load()`) that returns a tuple of your config, data, and renderer **classes**
(the type `bullpen.api.PLUGIN_DEFINITION`).

Then, expose this function as an entrypoint under the `'bullpen.mlbled.plugin'` key.
See `example-plugin/pyproject.toml` for the full syntax.


### Utilities

Bullpen provides a few helpers

#### Logging

`bullpen.logging.LOGGER` gives a way to provide information to the user based on their `debug` setting.

#### Scrolling text

`bullpen.util.scrolling_text` is our utility for rendering text that is too large to fit on the screen.
