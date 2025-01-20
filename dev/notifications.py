# %%
import panel as pn
pn.extension(notifications=True)
pn.template.MaterialTemplate(
    main=pn.io.notifications.NotificationArea.demo()
).servable()