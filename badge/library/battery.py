from machine import Pin, ADC
import config


class Meter:
    def __init__(
        self,
        POWER_BAR_LENGTH=10,
        FULLY_CHARGED_ADC_VALUE=2404,
        DEPLETED_ADC_VALUE=1500,
        MAX_VOLTAGE=2.4,
    ):
        self.MAX_VOLTAGE = MAX_VOLTAGE
        self.FULLY_CHARGED_ADC_VALUE = FULLY_CHARGED_ADC_VALUE
        self.DEPLETED_ADC_VALUE = DEPLETED_ADC_VALUE
        self.POWER_BAR_LENGTH = POWER_BAR_LENGTH
        self.adc = ADC(Pin(config.ADC_PIN))

    def info(self):
        # Read the ADC value directly:
        adc_value = self.adc.read()

        if adc_value >= 2404:
            percentage = 100
        elif adc_value <= 1500:
            percentage = 0
        else:
            percentage = ((adc_value - 1500) / (2404 - 1500)) * 100

        return "{:.2f}".format(percentage)
