param(
    [string[]] $FixturePath = @(
        (Join-Path $PSScriptRoot '..\fixtures\m1\binance_cases.json'),
        (Join-Path $PSScriptRoot '..\fixtures\m1\okx_cases.json')
    )
)

$ErrorActionPreference = 'Stop'
$allowedExchanges = @('binance', 'okx')
$allowedQuality = @('normal', 'delayed', 'missing', 'out_of_order', 'invalid')
$accepted = 0
$rejected = 0
$expectedCases = 0
$replayRows = @()

function Assert-Condition([bool] $Condition, [string] $Message) {
    if (-not $Condition) { throw "fixture validation failed: $Message" }
}

foreach ($path in $FixturePath) {
    $bundle = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    Assert-Condition ($bundle.schema_version -eq 'm1.v1') "$path schema version"
    Assert-Condition ($allowedExchanges -contains $bundle.exchange) "$path exchange"
    $expectedCases += @($bundle.cases).Count

    foreach ($case in $bundle.cases) {
        $recordsById = @{}
        foreach ($record in @($case.records)) {
            Assert-Condition (-not $recordsById.ContainsKey($record.record_id)) "$($case.case_id) duplicate record id"
            $recordsById[$record.record_id] = $record
            Assert-Condition ($record.symbol -eq 'BTCUSDT') "$($record.record_id) symbol"
            Assert-Condition ($record.market_type -eq 'usdt_perpetual') "$($record.record_id) market type"
            Assert-Condition ($allowedQuality -contains $record.data_quality) "$($record.record_id) quality"
            $replayRows += "$($bundle.exchange)|$($case.case_id)|$($record.record_id)|$($record.event_time)|$($record.data_quality)"
            $event = [DateTimeOffset]::Parse($record.event_time)
            $available = [DateTimeOffset]::Parse($record.available_time)
            $received = [DateTimeOffset]::Parse($record.received_time)
            Assert-Condition ($available -ge $event) "$($record.record_id) availability before event"
            Assert-Condition ($received -ge $available) "$($record.record_id) receipt before availability"

            if ($record.data_quality -eq 'invalid') {
                $rejected++
                continue
            }

            if ($record.record_type -eq 'candle') {
                Assert-Condition ($record.high -ge $record.open -and $record.high -ge $record.close -and $record.low -le $record.open -and $record.low -le $record.close -and $record.high -ge $record.low) "$($record.record_id) candle range"
                Assert-Condition ($record.base_volume -ge 0 -and $record.quote_volume -ge 0 -and $record.trade_count -ge 0) "$($record.record_id) candle quantities"
            }
            if ($record.record_type -eq 'metrics') {
                Assert-Condition ($record.base_volume -ge 0 -and $record.quote_volume -ge 0) "$($record.record_id) metric volumes"
                if ($record.data_quality -eq 'missing') {
                    Assert-Condition ($null -eq $record.open_interest -and $null -eq $record.funding_rate) "$($record.record_id) missing fields must be null"
                }
            }
            if ($record.record_type -eq 'data_health') {
                Assert-Condition ($record.usable_for_signal -eq $false -or $record.data_quality -eq 'normal') "$($record.record_id) unhealthy record usable"
            }
            $accepted++
        }

        foreach ($recordId in @($case.arrival_order)) {
            Assert-Condition ($recordsById.ContainsKey($recordId)) "$($case.case_id) arrival id missing"
        }

        $sorted = @($case.records | Sort-Object { [DateTimeOffset]::Parse($_.event_time) }, { [DateTimeOffset]::Parse($_.available_time) }, record_id)
        $expected = @($sorted | ForEach-Object record_id)
        $actual = @($case.arrival_order)
        if ($case.case_id -like '*out-of-order') {
            Assert-Condition (($actual -join ',') -ne ($expected -join ',')) "$($case.case_id) must demonstrate out-of-order arrival"
        }
    }
}

$canonicalReplay = (($replayRows | Sort-Object) -join "`n")
$digestBytes = [System.Text.Encoding]::UTF8.GetBytes($canonicalReplay)
$digest = [System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create().ComputeHash($digestBytes))).Replace('-', '').ToLowerInvariant()
Write-Output "M1 fixture validation passed: bundles=$($FixturePath.Count), cases=$expectedCases, accepted=$accepted, rejected=$rejected, replay_digest=$digest"
