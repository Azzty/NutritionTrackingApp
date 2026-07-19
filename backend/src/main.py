import flet as ft
import src.services.livsmedelsverket_client as lmv

db_client = lmv.LivsmedelsverketClient()


class IngredientInfoContainer(ft.Container):
    def __init__(self, ingredient: lmv.Ingredient, **kwargs):
        super().__init__(**kwargs)
        self.ingredient = ingredient
        self.content = ft.Text(value=str(self.ingredient.name))


def main(page: ft.Page):
    page.title = "Livsmedelsverket DB search"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    def toggle_semantics(e: ft.KeyboardEvent):
        if e.shift and e.key == "S":
            page.show_semantics_debugger = not page.show_semantics_debugger
            page.update()

    page.on_keyboard_event = toggle_semantics

    results_view = ft.Column()
    detailed_ingredients_view = ft.Column()

    page.bottom_sheet = ft.BottomSheet(
        content=ft.Container(content=ft.Text("Ingen produkt vald."), padding=20)
    )

    def _show_ingredient_nutrition(e):
        ingredient = e.control.ingredient
        page.bottom_sheet.content = ft.Column(
            controls=[
                ft.Text(value=f"Namn: {ingredient.name}"),
                ft.Text(value=f"Fett: {ingredient.fat}"),
                ft.Text(value=f"Protein: {ingredient.protein}"),
                ft.Text(value=f"Kolhydrater: {ingredient.carbs}"),
                ft.Text(value=f"Kalorier: {ingredient.calories}"),
            ]
        )
        page.show_dialog(page.bottom_sheet)

    def _update_results(e):
        query = search_input.value
        results = db_client.search_foods_by_name(query)
        results_view.controls = []
        for result in results:
            results_view.controls.append(
                IngredientInfoContainer(result, on_click=_show_ingredient_nutrition)
            )

    search_input = ft.TextField(
        value="",
        text_align=ft.TextAlign.RIGHT,
        width=400,
        hint_text="Sök",
        on_change=_update_results,
    )

    page.add(
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[search_input]),
        results_view,
        detailed_ingredients_view,
    )


ft.run(main, view=ft.AppView.WEB_BROWSER)
