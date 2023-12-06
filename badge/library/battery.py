from machine import Pin, ADC
import config


class Meter:
    def __init__(
        self,
        FULLY_CHARGED_ADC_VALUE,
        DEPLETED_ADC_VALUE,
        MAX_VOLTAGE=2.4,
        power_bar_length=10,
    ):
        self.FULLY_CHARGED_ADC_VALUE = FULLY_CHARGED_ADC_VALUE
        self.DEPLETED_ADC_VALUE = DEPLETED_ADC_VALUE
        self.MAX_VOLTAGE = MAX_VOLTAGE
        self.power_bar_length = power_bar_length
        self.adc = ADC(Pin(config.ADC_PIN))

    def info(self):
        # Read the ADC value:
        adc_value = self.adc.read()

        # Calculate voltage based on the provided ADC value:
        voltage = (
            (adc_value - self.DEPLETED_ADC_VALUE)
            / (self.FULLY_CHARGED_ADC_VALUE - self.DEPLETED_ADC_VALUE)
        ) * self.MAX_VOLTAGE

        # Calculate percentage based on the voltage:
        percentage = (voltage / self.MAX_VOLTAGE) * 100

        # Ensure the percentage does not exceed 100%:
        percentage = min(percentage, 100)

        return "{:.2f}".format(percentage)
