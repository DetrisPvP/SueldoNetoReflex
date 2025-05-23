import reflex as rx

class State(rx.State):
    """Define el estado de la aplicación y la lógica de cálculo."""

    #constantes del sistema de calculo
    TASA_TSS: float = 0.0591  # Seguridad social
    TASA_BONIFICACION: float = 0.0833  # Bonificación

    #limites y tasas ISR anuales de la DGII (para RD$)
    LIMITE_EXENTO_ANUAL: float = 416220.00
    LIMITE_TRAMO1_ANUAL: float = 624329.00
    LIMITE_TRAMO2_ANUAL: float = 867123.00

    TASA_ISR_1: float = 0.15
    TASA_ISR_2: float = 0.20
    TASA_ISR_3: float = 0.25

    #variables de entrada y salida
    sueldo_bruto: str = "0.0"
    otros_descuentos: str = "0.0"

    # conversion de float
    @rx.var
    def sueldo_bruto_float(self) -> float:
        try:
            return float(self.sueldo_bruto)
        except ValueError:
            return 0.0

    @rx.var
    def otros_descuentos_float(self) -> float:
        try:
            return float(self.otros_descuentos)
        except ValueError:
            return 0.0

    #calculos 
    @rx.var
    def _calcular_descuento_tss(self) -> float:
        return self.sueldo_bruto_float * self.TASA_TSS

    @rx.var
    def _calcular_bonificacion(self) -> float:
        return self.sueldo_bruto_float * self.TASA_BONIFICACION

    @rx.var
    def _calcular_isr(self) -> float:
        ingreso_anual = self.sueldo_bruto_float * 12
        ingreso_anual -= ingreso_anual * self.TASA_TSS
        ingreso_anual -= ingreso_anual * self.TASA_BONIFICACION

        if ingreso_anual <= self.LIMITE_EXENTO_ANUAL:
            return 0.0
        elif ingreso_anual <= self.LIMITE_TRAMO1_ANUAL:
            return (ingreso_anual - self.LIMITE_EXENTO_ANUAL) * self.TASA_ISR_1 / 12
        elif ingreso_anual <= self.LIMITE_TRAMO2_ANUAL:
            tramo1 = (self.LIMITE_TRAMO1_ANUAL - self.LIMITE_EXENTO_ANUAL) * self.TASA_ISR_1
            tramo2 = (ingreso_anual - self.LIMITE_TRAMO1_ANUAL) * self.TASA_ISR_2
            return (tramo1 + tramo2) / 12
        else:
            tramo1 = (self.LIMITE_TRAMO1_ANUAL - self.LIMITE_EXENTO_ANUAL) * self.TASA_ISR_1
            tramo2 = (self.LIMITE_TRAMO2_ANUAL - self.LIMITE_TRAMO1_ANUAL) * self.TASA_ISR_2
            tramo3 = (ingreso_anual - self.LIMITE_TRAMO2_ANUAL) * self.TASA_ISR_3
            return (tramo1 + tramo2 + tramo3) / 12

    @rx.var
    def _calcular_sueldo_neto(self) -> float:
        return (
            self.sueldo_bruto_float
            - self._calcular_descuento_tss
            - self._calcular_isr
            - self.otros_descuentos_float
            + self._calcular_bonificacion
        )

    #formato en string 
    @rx.var
    def sueldo_bruto_str(self) -> str:
        return f"RD$ {self.sueldo_bruto_float:,.2f}"

    @rx.var
    def descuento_tss_str(self) -> str:
        return f"RD$ {self._calcular_descuento_tss:,.2f}"

    @rx.var
    def isr_str(self) -> str:
        return f"RD$ {self._calcular_isr:,.2f}"

    @rx.var
    def otros_descuentos_str(self) -> str:
        return f"RD$ {self.otros_descuentos_float:,.2f}"

    @rx.var
    def bonificacion_str(self) -> str:
        return f"RD$ {self._calcular_bonificacion:,.2f}"

    @rx.var
    def sueldo_neto_str(self) -> str:
        return f"RD$ {self._calcular_sueldo_neto:,.2f}"

    def reset_form(self):
        self.sueldo_bruto = "0.0"
        self.otros_descuentos = "0.0"


@rx.page(title="Calculadora de Sueldo Neto RD")
def index():
    return rx.center(
        rx.vstack(
            rx.heading("Calculadora de Sueldo Neto (RD)", size="8"),
            rx.text("Ingresa los valores para calcular tu sueldo neto."),
            rx.divider(),

            rx.form(
                rx.vstack(
                    rx.vstack(
                        rx.text("Sueldo Bruto Mensual (RD$):"),
                        rx.input(
                            id="sueldo_bruto",
                            type="number",
                            placeholder="Ej: 50000.00",
                            value=State.sueldo_bruto,
                            on_change=State.set_sueldo_bruto,
                            step="0.01",
                            min="0"
                        ),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Otros Descuentos (RD$):"),
                        rx.input(
                            id="otros_descuentos",
                            type="number",
                            placeholder="Ej: 0.00",
                            value=State.otros_descuentos,
                            on_change=State.set_otros_descuentos,
                            step="0.01",
                            min="0"
                        ),
                        width="100%",
                    ),
                    rx.button("Resetear Campos", on_click=State.reset_form, color_scheme="red"),
                    spacing="3",
                    width="100%"
                ),
                width="100%"
            ),

            rx.divider(),

            rx.vstack(
                rx.text("Resultados:", font_weight="bold", size="6"),
                rx.hstack(rx.text("Sueldo Bruto:"), rx.spacer(), rx.text(State.sueldo_bruto_str), width="100%"),
                rx.hstack(rx.text("Descuento TSS (5.91%):"), rx.spacer(), rx.text(State.descuento_tss_str), width="100%"),
                rx.hstack(rx.text("Retención ISR:"), rx.spacer(), rx.text(State.isr_str), width="100%"),
                rx.hstack(rx.text("Otros Descuentos:"), rx.spacer(), rx.text(State.otros_descuentos_str), width="100%"),
                rx.hstack(rx.text("Bonificación (8.33%):"), rx.spacer(), rx.text(State.bonificacion_str), width="100%"),
                rx.hstack(
                    rx.text("Sueldo Neto:", font_weight="bold", color_scheme="green"),
                    rx.spacer(),
                    rx.text(State.sueldo_neto_str, font_weight="extrabold", color_scheme="green", size="6"),
                    width="100%",
                ),
                spacing="2",
                width="100%"
            ),
            spacing="5",
            padding="5",
            max_width="600px",
            width="100%",
        )
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
        gray_color="slate",
        radius="small",
        scaling="95%",
    ),
)

