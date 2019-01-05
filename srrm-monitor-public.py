import lxml.etree as etree
import requests
import datetime

requests.packages.urllib3.disable_warnings()

__author__ = 'Tighe Schlottog || tschlottog@paloaltonetworks.com'
__description__ = 'Pull the stats from the show running resource-monitor on the firewall in a structured manner'
__version__ = '1.0'

#  These are the configurable variables
MAX_CPU = 3                    # Max CPU percent, this is your mark to start throwing errors
time_window = 15                # Numeric value of length time slices wanted for the measurement
time_measure = 'minute'         # This is either second, minute, hour, day, week
fw_host = ''        # This is the Management (or in-path Management) IP of the firewall
CSV_OUT = True                  # This is used to define whether or not to dump the data out to a csv formated document
csv_file = 'srrm-stats.csv'
api_key = ''   # This is the API Key used to access the firewall


#  Nothing past here needs to be configured
srrm_params = {'type': 'op', 'cmd': '<show><running><resource-monitor><%s><last>%d</last></%s></resource-monitor></running></show>' % (time_measure, time_window, time_measure), 'key': api_key}
srrm = requests.get('https://%s/api' % fw_host, params=srrm_params, verify=False)
print srrm.content
srrm_stats = {}
time_now = datetime.datetime.now().strftime('%Y/%m/%d@%H:%M:%S')

if srrm.status_code == 200:
    root = etree.fromstring(srrm.content)
    dp_xpath = root.xpath('.//data-processors')
    dp_list = []
    for dps in dp_xpath:
        for dp in dps:
            dp_list.append(dp.tag)

    for dp in dp_list:
        if dp not in srrm_stats:
            srrm_stats[dp] = {}
            srrm_stats[dp]['cpu_avgs'] = {}
            srrm_stats[dp]['cpu_maxs'] = {}
        cpu_avgs = root.xpath('.//data-processors/%s/%s/cpu-load-average/entry' % (dp, time_measure))
        for entry in cpu_avgs:
            for item in entry:
                if item.tag == 'coreid':
                    core_id = item.text
                if item.tag == 'value':
                    core_data = item.text
            srrm_stats[dp]['cpu_avgs'][core_id] = core_data
        cpu_maxs = root.xpath('.//data-processors/%s/%s/cpu-load-maximum/entry' % (dp, time_measure))
        for entry in cpu_maxs:
            for item in entry:
                if item.tag == 'coreid':
                    core_id = item.text
                if item.tag == 'value':
                    core_data = item.text
            srrm_stats[dp]['cpu_maxs'][core_id] = core_data

if CSV_OUT:
    csv_out = open(csv_file, 'a')

for DP in srrm_stats:
    for type in srrm_stats[DP]:
        for core in srrm_stats[DP][type]:
            cpu_data = [int(x) for x in srrm_stats[DP][type][core].split(',')]
            for idx, val in enumerate(cpu_data):
                if CSV_OUT:
                    csv_out.write('%s,%s %s,%s,%s,%s,%s\n' % (time_now, time_window, time_measure, type, DP, core, srrm_stats[DP][type][core]))
                if val > MAX_CPU:
                    print '%s | %s | Core %s | %d CPU Utilization | %d minutes ago' % (DP, type, core, val, idx)
