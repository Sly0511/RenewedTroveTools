from flet import View, Row, VerticalDivider
from flet_core.icons import MENU_BOOK_SHARP

from controllers import MasteryController


class MasteryView(View):
    route = "/mastery"
    title = "Mastery"
    icon = MENU_BOOK_SHARP
    has_tab = True

    def __init__(self, page):
        ctrl = MasteryController(page=page)
        super().__init__(
            route=self.route,
            controls=[
                ctrl.points_input,
                ctrl.level_input,
                Row(
                    controls=[
                        ctrl.mastery_buffs,
                        VerticalDivider(),
                        ctrl.geode_buffs,
                    ],
                    vertical_alignment="start",
                ),
            ],
        )
