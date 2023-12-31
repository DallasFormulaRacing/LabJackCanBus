canMessages = {
    '218099784': ['RPM', 'TPS', 'Fuel Open Time', 'Ignition Angle'],
    '218100040': ['Barometer', 'MAP', 'Lambda', 'Pressure Type'],
    '218100296': ['Analog Input #1', 'Analog Input #2', 'Analog Input #3', 'Analog Input #4'],
    '218100552': ['Analog Input #5', 'Analog Input #6', 'Analog Input #7', 'Analog Input #8'],
    '218100808': ['Frequency 1', 'Frequency 2', 'Frequency 3', 'Frequency 4'],
    '218101064': ['Battery Volt', 'Air Temp', 'Coolant Temp', 'Temp Type'],
    '218101320': ['Analog Input #5', 'Analog Input #7'],
    '218101576': ['RPM Rate', 'TPS Rate', 'MAP Rate', 'MAF Load Rate'],
    '218101832': ['Lambda #1 Measured', 'Lambda #2 Measured', 'Target Lambda'],
    '218102088': ['PWM Duty Cycle #1', 'PWM Duty Cycle #2', 'PWM Duty Cycle #2', 'PWM Duty Cycle #3', 'PWM Duty Cycle #4', 'PWM Duty Cycle #5', 'PWM Duty Cycle #6', 'PWM Duty Cycle #7', 'PWM Duty Cycle #8'],
    '218102344': ['Percent Slip', 'Driven Wheel Rate of Change', 'Desired Value'],
    '218102600': ['Driven AVG Wheel Speed', 'Non-Driven AVG Wheel Speed', 'Ignition Compensation', 'Ignitiion Cut Percentage'],
    '218102856': ['Driven Wheel Speed #1', 'Driven Wheel Speed #2', 'Non-Driven Wheel Speed #1', 'Non-Driven Wheel Speed #2'],
    '218103112': ['Fuel Comp-Accel', 'Fuel Comp-Starting', 'Fuel Comp-Air Temp', 'Fuel Comp-Coolant Temp'],
    '218103368': ['Fuel Comp-Barometer', 'Fuel Comp-MAP'],
    '218099784': ['Ignition Comp-Air Temp', 'Ignition Comp-Coolant Temp', 'Ignition Comp-Barometer', 'Ignition Comp-MAP'],
}

can_messages_cols = ["time",
                     "218099784",
                     "218100040",
                     "218100296",
                     "218100552",
                     "218100808",
                     "218101064",
                     "218101320",
                     "218101576",
                     "218101832",
                     "218102088",
                     "218102344",
                     "218102600",
                     "218102856",
                     "218103112",
                     "218103368",
                     "218091592"]

canMessageSort = {
    218099784: 0,
    218100040: 1,
    218100296: 2,
    218100552: 3,
    218100808: 4,
    218101064: 5,
    218101320: 6,
    218101576: 7,
    218101832: 8,
    218102088: 9,
    218102344: 10,
    218102600: 11,
    218102856: 12,
    218103112: 13,
    218103368: 14,
    218091592: 15
}
